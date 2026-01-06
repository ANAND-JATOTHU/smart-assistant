"""
Intent Extraction
Extract structured intent from user input using LLM
"""

import json
import re
from typing import Dict, Any, Optional
from models.base import BaseLLM


class IntentExtractor:
    """Extract intent from user input"""
    
    def __init__(self, llm: Optional[BaseLLM] = None):
        """
        Initialize intent extractor
        
        Args:
            llm: Language model for intent extraction
        """
        self.llm = llm
    
    def extract(self, user_input: str) -> Dict[str, Any]:
        """
        Extract intent from user input using rule-based detection
        
        Args:
            user_input: User's message
        
        Returns:
            Intent dict with:
                - action: str (e.g., 'open_application', 'search_web')
                - target: str (e.g., 'chrome', 'weather')
                - parameters: dict
                - confidence: float (0.0 - 1.0)
                - is_command: bool
        """
        # Use rule-based extraction (fast and reliable)
        return self._rule_based_extraction(user_input)
    
    def _rule_based_extraction(self, user_input: str) -> Dict[str, Any]:
        """Simple rule-based intent extraction"""
        input_lower = user_input.lower()
        
        # Open application
        if any(word in input_lower for word in ['open', 'launch', 'start']):
            for app in ['chrome', 'firefox', 'notepad', 'calculator', 'explorer']:
                if app in input_lower:
                    return {
                        'action': 'open_application',
                        'target': app,
                        'parameters': {},
                        'confidence': 0.8,
                        'is_command': True
                    }
        
        # Close application
        if any(word in input_lower for word in ['close', 'quit', 'exit']):
            for app in ['chrome', 'firefox', 'notepad']:
                if app in input_lower:
                    return {
                        'action': 'close_application',
                        'target': app,
                        'parameters': {},
                        'confidence': 0.8,
                        'is_command': True
                    }
        
        # Volume control
        if 'volume' in input_lower:
            if 'up' in input_lower or 'increase' in input_lower:
                target = 'up'
            elif 'down' in input_lower or 'decrease' in input_lower:
                target = 'down'
            elif 'mute' in input_lower:
                target = 'mute'
            else:
                target = 'get'
            
            return {
                'action': 'control_volume',
                'target': target,
                'parameters': {},
                'confidence': 0.9,
                'is_command': True
            }
        
        # Screenshot
        if 'screenshot' in input_lower or 'screen shot' in input_lower:
            return {
                'action': 'take_screenshot',
                'target': '',
                'parameters': {},
                'confidence': 0.9,
                'is_command': True
            }
        
        # Web search
        if any(word in input_lower for word in ['search', 'google', 'look up']):
            # Extract search query
            query = user_input
            for word in ['search for', 'google', 'look up', 'search']:
                query = query.replace(word, '').strip()
            
            return {
                'action': 'search_web',
                'target': query,
                'parameters': {},
                'confidence': 0.7,
                'is_command': True
            }
        
        # Not a command
        return {
            'action': 'conversation',
            'target': '',
            'parameters': {},
            'confidence': 0.5,
            'is_command': False
        }
    
    def _llm_based_extraction(self, user_input: str) -> Dict[str, Any]:
        """LLM-based intent extraction"""
        prompt = f"""Extract the intent from this user message. Return ONLY a JSON object.

User message: "{user_input}"

Available actions:
- open_application (target: app name)
- close_application (target: app name)
- search_file (target: search query)
- open_file (target: file path)
- open_url (target: URL)
- search_web (target: search query)
- take_screenshot
- control_volume (target: up/down/mute/unmute or number)
- conversation (for general chat)

Return JSON format:
{{
  "action": "action_name",
  "target": "target_value",
  "parameters": {{}},
  "confidence": 0.0-1.0,
  "is_command": true/false
}}

JSON:"""
        
        try:
            response = self.llm.generate(prompt, temperature=0.1, max_tokens=150)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                intent = json.loads(json_match.group())
                return intent
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"❌ LLM extraction error: {e}")
            raise


if __name__ == "__main__":
    # Test intent extraction
    extractor = IntentExtractor()
    
    test_inputs = [
        "Open Chrome browser",
        "Increase the volume",
        "Take a screenshot",
        "Search for weather today",
        "What is the capital of France?"
    ]
    
    for inp in test_inputs:
        intent = extractor.extract(inp)
        print(f"\nInput: {inp}")
        print(f"Intent: {json.dumps(intent, indent=2)}")
