"""
Utility functions for the Firefly Analyzer
"""

from typing import Any, Dict, List, Union
import json


def normalize_value(value: Any) -> Any:
    """
    Normalize values for comparison by handling common type differences.
    
    Args:
        value: The value to normalize
        
    Returns:
        Normalized value
    """
    if isinstance(value, str):
        # Try to convert string numbers to actual numbers
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            pass
    
    return value


def normalize_tags(tags: Union[Dict, List]) -> Dict[str, Any]:
    """
    Normalize tags to a consistent dictionary format.
    
    Args:
        tags: Tags in various formats
        
    Returns:
        Normalized tags dictionary
    """
    if isinstance(tags, list):
        # Convert list of key-value pairs to dictionary
        return {item.get('Key', item.get('key', '')): item.get('Value', item.get('value', '')) 
                for item in tags if isinstance(item, dict)}
    elif isinstance(tags, dict):
        return tags
    else:
        return {}


def load_json_file(file_path: str) -> Union[Dict, List]:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file {file_path}: {e}")


def save_json_file(data: Union[Dict, List], file_path: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save the file
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_nested_value(obj: Dict[str, Any], key_path: str) -> Any:
    """
    Get a nested value from a dictionary using dot notation.
    
    Args:
        obj: Dictionary to search in
        key_path: Dot-separated path (e.g., "tags.totalAmount")
        
    Returns:
        The value at the specified path, or None if not found
    """
    keys = key_path.split('.')
    current = obj
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    
    return current


def set_nested_value(obj: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    Set a nested value in a dictionary using dot notation.
    
    Args:
        obj: Dictionary to modify
        key_path: Dot-separated path (e.g., "tags.totalAmount")
        value: Value to set
    """
    keys = key_path.split('.')
    current = obj
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
