"""
Parameter validation utilities
"""

from typing import Any, Dict, List, Optional, Union

def validate_numeric_range(
    value: Union[int, float], 
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    param_name: str = "value"
) -> None:
    """Validate numeric value is within range"""
    if min_value is not None and value < min_value:
        raise ValueError(f"{param_name} must be >= {min_value}")
    if max_value is not None and value > max_value:
        raise ValueError(f"{param_name} must be <= {max_value}")
        
def validate_required_params(params: Dict[str, Any], required: List[str]) -> None:
    """Validate required parameters are present and not None"""
    missing = [param for param in required if param not in params or params[param] is None]
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")
        
def validate_string_length(
    value: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    param_name: str = "value"
) -> None:
    """Validate string length is within range"""
    if min_length is not None and len(value) < min_length:
        raise ValueError(f"{param_name} must be at least {min_length} characters")
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"{param_name} must be at most {max_length} characters")
