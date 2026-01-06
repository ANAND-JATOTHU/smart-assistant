"""
Utility functions for Smart Assistant
Shared utilities across modules
"""

import urllib.request


def check_internet_connection(timeout: int = 2) -> bool:
    """
    Check if internet connection is available
    
    Args:
        timeout: Timeout in seconds
        
    Returns:
        bool: True if internet is available
    """
    try:
        urllib.request.urlopen('http://www.google.com', timeout=timeout)
        return True
    except:
        return False


def get_connection_status() -> str:
    """
    Get human-readable connection status
    
    Returns:
        str: "Online" or "Offline"
    """
    return "Online" if check_internet_connection() else "Offline"
