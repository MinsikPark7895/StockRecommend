"""
Utility functions for financial data collection.

Contains security-focused validation and helper functions.
"""

import re
import logging
from typing import Optional
from functools import wraps
import time

logger = logging.getLogger(__name__)


def validate_ticker_symbol(ticker: str) -> str:
    """
    Validate and sanitize ticker symbol.
    
    Security: Prevents injection attacks and ensures valid input format.
    
    Args:
        ticker: Stock ticker symbol to validate
        
    Returns:
        Uppercase, validated ticker symbol
        
    Raises:
        ValueError: If ticker is invalid
    """
    if not ticker:
        raise ValueError("Ticker symbol cannot be empty")
    
    if not isinstance(ticker, str):
        raise ValueError("Ticker symbol must be a string")
    
    # Remove whitespace
    ticker = ticker.strip().upper()
    
    # Validate format: 1-5 alphanumeric characters, optionally followed by .[A-Z]
    # Examples: AAPL, BRK.B, GOOGL
    pattern = r'^[A-Z0-9]{1,5}(\.[A-Z])?$'
    
    if not re.match(pattern, ticker):
        raise ValueError(
            f"Invalid ticker format: {ticker}. "
            "Ticker must be 1-5 uppercase letters/numbers, optionally with .[A-Z]"
        )
    
    # Additional security: Check for potentially dangerous characters
    dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>']
    if any(char in ticker for char in dangerous_chars):
        raise ValueError(f"Ticker contains invalid characters: {ticker}")
    
    return ticker


def validate_period(period: str) -> str:
    """
    Validate period parameter.
    
    Args:
        period: Period string ("annual" or "quarter")
        
    Returns:
        Lowercase, validated period string
        
    Raises:
        ValueError: If period is invalid
    """
    if not period:
        raise ValueError("Period cannot be empty")
    
    period_lower = period.lower().strip()
    
    if period_lower not in ["annual", "quarter"]:
        raise ValueError(f"Invalid period: {period}. Must be 'annual' or 'quarter'")
    
    return period_lower


def validate_limit(limit: int) -> int:
    """
    Validate limit parameter.
    
    Args:
        limit: Number of records to retrieve
        
    Returns:
        Validated limit value
        
    Raises:
        ValueError: If limit is invalid
    """
    if not isinstance(limit, int):
        raise ValueError("Limit must be an integer")
    
    if limit < 1:
        raise ValueError("Limit must be at least 1")
    
    if limit > 100:  # Reasonable upper bound to prevent abuse
        raise ValueError("Limit cannot exceed 100")
    
    return limit


def mask_api_key(api_key: Optional[str]) -> str:
    """
    Mask API key for logging purposes.
    
    Security: Prevents API key exposure in logs.
    
    Args:
        api_key: API key to mask
        
    Returns:
        Masked API key (shows only first 4 and last 4 characters)
    """
    if not api_key:
        return "None"
    
    if len(api_key) <= 8:
        return "****"
    
    return f"{api_key[:4]}...{api_key[-4:]}"


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error messages to prevent information leakage.
    
    Security: Removes sensitive information from error messages.
    
    Args:
        error: Exception object
        
    Returns:
        Sanitized error message safe for user display
    """
    error_msg = str(error)
    
    # Remove potential API keys from error messages
    # Pattern: looks for long alphanumeric strings that might be API keys
    api_key_pattern = r'\b[A-Za-z0-9]{20,}\b'
    error_msg = re.sub(api_key_pattern, '[REDACTED]', error_msg)
    
    # Remove file paths that might reveal system structure
    path_pattern = r'[A-Z]:\\[^\s]+|/[^\s]+'
    error_msg = re.sub(path_pattern, '[PATH_REDACTED]', error_msg)
    
    # Generic error message if original contains sensitive info
    sensitive_keywords = ['api_key', 'password', 'secret', 'token', 'credential']
    if any(keyword.lower() in error_msg.lower() for keyword in sensitive_keywords):
        return "An error occurred while processing the request. Please check logs for details."
    
    return error_msg


def rate_limit(max_calls: int = 5, period: float = 1.0):
    """
    Decorator for rate limiting API calls.
    
    Args:
        max_calls: Maximum number of calls allowed
        period: Time period in seconds
    """
    min_interval = period / max_calls
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator
