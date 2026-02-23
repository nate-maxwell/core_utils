import os
from pathlib import Path
from typing import Optional


def get_str(key: str, fallback: Optional[str] = None) -> Optional[str]:
    """
    Get an environment variable as a string.

    Args:
        key (str): The environment variable name.
        fallback (str): Value to return if the variable is not set.
            Defaults to None.
    Returns:
        Optional[str]: The value of the environment variable, or the fallback.
    """
    return os.environ.get(key, fallback)


def get_int(key: str, fallback: Optional[int] = None) -> Optional[int]:
    """
    Get an environment variable as an integer.
    Returns the fallback if the variable is not set or cannot be cast to int.

    Args:
        key (str): The environment variable name.
        fallback (int): Value to return if the variable is not set or invalid.
            Defaults to None.
    Returns:
        Optional[int]: The value cast to int, or the fallback.
    """
    value = os.environ.get(key)
    if value is None:
        return fallback
    try:
        return int(value)
    except ValueError:
        return fallback


def get_bool(key: str, fallback: Optional[bool] = None) -> Optional[bool]:
    """
    Get an environment variable as a boolean.
    Truthy string values: '1', 'true', 'yes', 'on' (case-insensitive).
    Falsy string values: '0', 'false', 'no', 'off' (case-insensitive).
    Returns the fallback if the variable is not set or does not match either set.

    Args:
        key (str): The environment variable name.
        fallback (bool): Value to return if the variable is not set or invalid.
            Defaults to None.
    Returns:
        Optional[bool]: The value cast to bool, or the fallback.
    """
    value = os.environ.get(key)
    if value is None:
        return fallback
    if value.lower() in ("1", "true", "yes", "on"):
        return True
    if value.lower() in ("0", "false", "no", "off"):
        return False
    return fallback


def get_path(key: str, fallback: Optional[Path] = None) -> Optional[Path]:
    """
    Get an environment variable as a resolved Path.
    Returns the fallback if the variable is not set.

    Args:
        key (str): The environment variable name.
        fallback (Path): Value to return if the variable is not set.
            Defaults to None.
    Returns:
        Optional[Path]: The value as a resolved Path, or the fallback.
    """
    value = os.environ.get(key)
    if value is None:
        return fallback
    return Path(value).resolve()


def get_list(
    key: str, fallback: Optional[list[str]] = None, delimiter: str = os.pathsep
) -> Optional[list[str]]:
    """
    Get an environment variable as a list of strings, split by a delimiter.
    Strips whitespace from each item and drops empty strings.

    Args:
        key (str): The environment variable name.
        fallback (list[str]): Value to return if the variable is not set.
            Defaults to None.
        delimiter (str): The character to split on. Defaults to os.pathsep.
    Returns:
        Optional[list[str]]: The split and stripped values, or the fallback.
    """
    value = os.environ.get(key)
    if value is None:
        return fallback
    return [item.strip() for item in value.split(delimiter) if item.strip()]


def require(keys: list[str]) -> None:
    """
    Assert that all given environment variables are set and non-empty.
    Raises an EnvironmentError listing every missing variable at once rather
    than failing one at a time, so the caller can fix all missing vars in a
    single pass.

    Args:
        keys (list[str]): The environment variable names that must be present.
    Raises:
        EnvironmentError: If one or more required variables are missing.
    """
    missing = [k for k in keys if not os.environ.get(k)]
    if missing:
        raise EnvironmentError(
            f"Required environment variable(s) not set: {', '.join(missing)}"
        )


def load_env_file(path: Path, overwrite: bool = False) -> None:
    """
    Load a .env file into os.environ.
    Supports:
        - KEY=VALUE pairs
        - Quoted values (single or double): KEY="hello world"
        - Inline comments: KEY=value  # this is ignored
        - Full-line comments (#) and blank lines are skipped.
        - Variable expansion: KEY2=$KEY1 or KEY2=${KEY1}

    Args:
        path (Path): Path to the .env file.
        overwrite (bool): If True, existing environment variables will be
            overwritten by values in the file. Defaults to False.
    Raises:
        FileNotFoundError: If the .env file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f".env file not found: {path}")

    for line in path.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, _, raw_value = line.partition("=")
        key = key.strip()
        raw_value = _strip_inline_comment(raw_value.strip())

        if (raw_value.startswith('"') and raw_value.endswith('"')) or (
            raw_value.startswith("'") and raw_value.endswith("'")
        ):
            raw_value = raw_value[1:-1]

        value = os.path.expandvars(raw_value)

        if overwrite or key not in os.environ:
            os.environ[key] = value


def _strip_inline_comment(value: str) -> str:
    """
    Strip an inline comment from a value string, respecting quoted regions.
    E.g. 'hello  # world' -> 'hello', '"hello # world"' -> '"hello # world"'.

    Args:
        value (str): The raw value string, potentially containing a comment.
    Returns:
        str: The value with any inline comment removed and trailing whitespace stripped.
    """
    in_quote = None
    for i, char in enumerate(value):
        if char in ('"', "'"):
            if in_quote is None:
                in_quote = char
            elif in_quote == char:
                in_quote = None
        elif char == "#" and in_quote is None:
            return value[:i].rstrip()

    return value
