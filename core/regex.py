"""
Pipeline Regex Utility Library

A collection of regex and other substring parsing utility functions.
"""

import os
import re
from typing import Optional


def get_file_version_number(file_name: str) -> Optional[str]:
    """
    Gets the integer version number of a file whose name
    ends with the standard version suffix: '_v###.ext',
    if it exists, otherwise returns None.

    Example file name: 'GhostA_anim_v001.ma'

    The suffix's number padding can be any length.

    Args:
        file_name (str): The file name to search.

    Returns:
        int: The integer version number.
    """
    temp = re.search(r"_v(\d+)\..*$", file_name)
    return temp.group(1) if temp else None


def is_path_like(value: str) -> bool:
    """
    Heuristically determine if a string looks like a Windows file or directory
    path.

    Args:
        value (str): The string to evaluate.
    Returns:
        bool: True if the string looks like a path, False otherwise.
    """
    if not isinstance(value, str):
        return False

    # Check for Windows drive-letter root (e.g. C:\ or D:/)
    if re.match(r"^[a-zA-Z]:[\\/]", value):
        return True

    # Check for UNC path (e.g. \\server\share)
    if value.startswith("\\\\"):
        return True

    # Relative Windows-style path (starts with .\ or ..\)
    if value.startswith((".\\", "..\\")):
        return True

    # Contains backslashes or forward slashes
    if "\\" in value or "/" in value:
        return True

    # Looks like a filename with an extension
    _, ext = os.path.splitext(value)
    if ext and len(ext) <= 7:
        return True

    return False


# -----Casing------------------------------------------------------------------


def pascal_to_snake(s: str) -> str:
    """Converts PascalCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def pascal_to_camel(s: str) -> str:
    """Converts PascalCase to camelCase."""
    return s[0].lower() + s[1:] if s else s


def camel_to_snake(s: str) -> str:
    """Converts camelCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def camel_to_pascal(s: str) -> str:
    """Converts camelCase to PascalCase."""
    return s[0].upper() + s[1:] if s else s


def snake_to_pascal(s: str) -> str:
    """Converts snake_case to PascalCase."""
    return "".join(word.capitalize() for word in s.split("_") if word)


def snake_to_camel(s: str) -> str:
    """Converts snake_case to camelCase."""
    words = [w for w in s.split("_") if w]
    return (
        words[0].lower() + "".join(w.capitalize() for w in words[1:]) if words else ""
    )
