import os
import re
from typing import Optional


def get_trailing_numbers_as_string(s: str) -> Optional[str]:
    """
    Gets a string of digits from the end of a string.
    String should not contain file extension.

    Args:
        s (str): The string the search.

    Returns:
        Optional[str]: The string og digits at the end of the string if one\
            exists. Returns None if no digits exists.
    """
    temp = re.search(r"\d+$", s)
    return str(temp.group()) if temp else None


def get_trailing_numbers_as_int(s: str) -> Optional[int]:
    """
    Gets the integer from the end of a string.
    String should not contain file extension.

    Args:
        s (str): The string the search.

    Returns:
        Optional[int]: The integer at the end of the string if one exists.
        Returns None if no integer exists.
    """
    try:
        return int(get_trailing_numbers_as_string(s))
    except (TypeError, ValueError):
        return None


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


def validation_no_special_chars(string: str) -> bool:
    """
    Checks a string to see if it contains non-alpha-numeric or non-underscore characters.
    Will return True if the string contains no special characters. Will return False
    if the string contains special characters or is an empty string.

    Args:
        string (str): The string to check against.

    Returns:
        bool: Whether the string contains no special characters.

    Notes:
        A common gotcha is that whitespace counts as a special character.
    """
    m = re.match(r"^[a-zA-Z0-9_]*$", string)
    if m and string != "":
        return True
    else:
        return False


def natural_sort_strings(items: list[str]):
    """
    Sort the given list in the way that humans expect.

    Args:
        list[str]: The list of strings to sort.
    """
    # Copied from studio library
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split(r"([0-9]+)", key)]
    items.sort(key=alphanum_key)


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
