"""
Safety Validator
Validate and confirm dangerous actions
"""

from typing import Dict, Any, List


class SafetyValidator:
    """Validate tool execution for safety"""
    
    # Dangerous actions that require confirmation
    DANGEROUS_ACTIONS = [
        'delete_file',
        'close_application',
        'shutdown',
        'restart'
    ]
    
    # Actions that should never be auto-executed
    FORBIDDEN_ACTIONS = [
        'format_disk',
        'delete_system_file'
    ]
    
    def __init__(self, require_confirmation: bool = True):
        """
        Initialize validator
        
        Args:
            require_confirmation: Require confirmation for dangerous actions
        """
        self.require_confirmation = require_confirmation
    
    def validate(self, intent: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate intent for safety
        
        Args:
            intent: Intent dict
        
        Returns:
            (is_safe, reason)
        """
        action = intent.get('action', '')
        
        # Check forbidden actions
        if action in self.FORBIDDEN_ACTIONS:
            return False, f"Action '{action}' is forbidden for safety reasons"
        
        # Check dangerous actions
        if action in self.DANGEROUS_ACTIONS and self.require_confirmation:
            return False, f"Action '{action}' requires user confirmation"
        
        # Check confidence threshold
        confidence = intent.get('confidence', 0.0)
        if confidence < 0.6:
            return False, f"Low confidence ({confidence:.2f}), please rephrase"
        
        return True, "Safe to execute"
    
    def needs_confirmation(self, intent: Dict[str, Any]) -> bool:
        """Check if intent needs confirmation"""
        action = intent.get('action', '')
        return action in self.DANGEROUS_ACTIONS


if __name__ == "__main__":
    # Test validator
    validator = SafetyValidator()
    
    test_intents = [
        {'action': 'open_application', 'confidence': 0.9},
        {'action': 'delete_file', 'confidence': 0.9},
        {'action': 'search_web', 'confidence': 0.4},
    ]
    
    for intent in test_intents:
        is_safe, reason = validator.validate(intent)
        print(f"Intent: {intent['action']}")
        print(f"  Safe: {is_safe}, Reason: {reason}\n")
