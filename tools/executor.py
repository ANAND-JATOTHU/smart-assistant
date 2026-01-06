"""
Tool Executor
Manages and executes tools with validation
"""

from typing import Dict, Any, Optional, List
from .base import Tool
from .applications import ApplicationTool
from .files import FileTool
from .system import SystemTool
from .browser import BrowserTool


class ToolExecutor:
    """Execute tools with validation and safety checks"""
    
    def __init__(self):
        """Initialize tool executor"""
        self.tools: Dict[str, Tool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools"""
        self.register_tool(ApplicationTool())
        self.register_tool(FileTool())
        self.register_tool(SystemTool())
        self.register_tool(BrowserTool())
    
    def register_tool(self, tool: Tool):
        """Register a tool"""
        self.tools[tool.name] = tool
        print(f"✅ Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [tool.get_info() for tool in self.tools.values()]
    
    def execute(
        self,
        tool_name: str,
        params: Dict[str, Any],
        skip_confirmation: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a tool
        
        Args:
            tool_name: Name of tool to execute
            params: Tool parameters
            skip_confirmation: Skip confirmation for dangerous tools
        
        Returns:
            Execution result
        """
        tool = self.get_tool(tool_name)
        
        if not tool:
            return {
                'success': False,
                'error': f'Tool not found: {tool_name}'
            }
        
        # Check if confirmation needed
        if tool.requires_confirmation and not skip_confirmation:
            return {
                'success': False,
                'error': 'Confirmation required',
                'requires_confirmation': True,
                'tool_info': tool.get_info()
            }
        
        # Validate parameters
        is_valid, error = tool.validate_params(**params)
        if not is_valid:
            return {
                'success': False,
                'error': f'Invalid parameters: {error}'
            }
        
        # Execute tool
        try:
            result = tool.execute(**params)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': f'Execution error: {str(e)}'
            }
    
    def execute_from_intent(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool from intent JSON
        
        Args:
            intent: Intent dict with 'action', 'target', 'parameters'
        
        Returns:
            Execution result
        """
        action = intent.get('action')
        target = intent.get('target')
        params = intent.get('parameters', {})
        
        # Map action to tool
        tool_mapping = {
            'open_application': ('application_control', {'action': 'open', 'app_name': target}),
            'close_application': ('application_control', {'action': 'close', 'app_name': target}),
            'search_file': ('file_operations', {'action': 'search', 'query': target}),
            'open_file': ('file_operations', {'action': 'open', 'path': target}),
            'open_url': ('browser_control', {'action': 'open', 'url': target}),
            'search_web': ('browser_control', {'action': 'search', 'query': target}),
            'take_screenshot': ('system_control', {'action': 'screenshot'}),
            'control_volume': ('system_control', {'action': 'volume', 'value': target}),
        }
        
        if action in tool_mapping:
            tool_name, tool_params = tool_mapping[action]
            tool_params.update(params)
            return self.execute(tool_name, tool_params)
        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}'
            }


if __name__ == "__main__":
    # Test tool executor
    executor = ToolExecutor()
    
    print("Available tools:")
    for tool in executor.list_tools():
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Test application tool
    print("\nTesting application tool:")
    result = executor.execute('application_control', {'action': 'open', 'app_name': 'notepad'})
    print(f"Result: {result}")
