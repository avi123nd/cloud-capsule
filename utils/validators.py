"""
Input validation utilities for Time Capsule Cloud
"""

import re
from datetime import datetime


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not email or not isinstance(email, str):
        return False, "Email is required"
    
    email = email.strip().lower()
    
    # Basic email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 254:  # RFC 5321 limit
        return False, "Email address too long"
    
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    
    Args:
        password: Password to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password is too long (maximum 128 characters)"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, ""


def validate_unlock_date(date_str: str) -> tuple[bool, str, datetime | None]:
    """
    Validate unlock date format and ensure it's in the future.
    
    Args:
        date_str: ISO format date string
        
    Returns:
        tuple: (is_valid, error_message, datetime_object)
    """
    if not date_str:
        return False, "Unlock date is required", None
    
    try:
        # Parse ISO format
        unlock_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        return False, "Invalid date format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)", None
    
    current_time = datetime.utcnow()
    
    if unlock_date <= current_time:
        return False, "Unlock date must be in the future", None
    
    # Prevent dates too far in the future (optional: 100 years)
    max_future = datetime.utcnow().replace(year=datetime.utcnow().year + 100)
    if unlock_date > max_future:
        return False, "Unlock date cannot be more than 100 years in the future", None
    
    return True, "", unlock_date


def validate_display_name(display_name: str) -> tuple[bool, str]:
    """
    Validate display name.
    
    Args:
        display_name: Display name to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if display_name is None:
        return True, ""  # Optional field
    
    if not isinstance(display_name, str):
        return False, "Display name must be a string"
    
    display_name = display_name.strip()
    
    if len(display_name) == 0:
        return True, ""  # Empty is allowed
    
    if len(display_name) > 100:
        return False, "Display name must be 100 characters or less"
    
    # Allow letters, numbers, spaces, and common special characters
    if not re.match(r'^[a-zA-Z0-9\s._-]+$', display_name):
        return False, "Display name contains invalid characters"
    
    return True, ""
