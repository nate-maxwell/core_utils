import re
from pathlib import Path
from typing import Optional
from typing import Union


def create_structure(structure: dict, destination: Path) -> None:
    """
    Create a directory structure from a given dict outline under the destination.
    Example:
    {
        'assets': {
            'model': {},
            'texture': {},
            'anim': {}
        },
        'config': {}
    }
    """
    # Separated from _create_structure to require a destination path, whereas
    # it is optional in the _recursive one.
    _create_structure(structure, destination)
    print(f"{structure} written to {destination}.")


def _create_structure(structure: dict, destination: Optional[Path] = None) -> None:
    """Recursively creates a folder form a nested dict."""
    if not destination.exists():
        destination.mkdir(exist_ok=True, parents=True)
    for k, v in structure.items():
        _create_structure(v, Path(destination, k))


def sort_path_list(path_objs: list[Path] = None) -> Optional[list[Path]]:
    """
    Alpha-numerically sorts a list of pathlib.Paths.

    Args:
        path_objs(list[Path]): The list of paths to sort.
    Returns:
        Optional[list[Path]]: The sorted list of paths or None if no list was
            provided.
    """
    if path_objs is None:
        return None

    def alphanum_key(path: Path) -> list[Union[int, str]]:
        """Natural sort key that handles numbers in filenames."""
        parts = re.split(r"([0-9]+)", path.as_posix())
        return [int(part) if part.isdigit() else part for part in parts]

    return sorted(path_objs, key=alphanum_key)


def delete_files_in_directory(directory_path: Path) -> None:
    """
    Delete all files in a directory.

    Args:
        directory_path (Path): Directory to delete files from.
    """
    try:
        for i in directory_path.iterdir():
            if i.is_file():
                i.unlink(missing_ok=True)
        print("All files deleted successfully.")
    except Exception:
        print("Error occurred while deleting files.")
        raise


def get_latest_version_file_from_dir(
    filepath: Path, extension: str, substring: Optional[str] = None
) -> Optional[Path]:
    """
    Gets the filename of the highest versioned file in a directory.

    Args:
        filepath (Path): The directory to search.
        extension (str): The file extension to filter by (with or without
            leading dot).
        substring (str): Optional substring the filename must contain.

    Returns:
        Optional[Path]: The filename of the highest versioned file, or None if
            no matches found.

    Note:
        Assumes version number is at the end of the base filename (before extension).
        Example: "file_v001.ext", "shot_042.ext"
    """
    ext = extension if extension.startswith(".") else f".{extension}"

    contents = filepath.iterdir()
    if not contents:
        return None

    candidates = [
        f
        for f in contents
        if f.suffix == ext and (substring is None or substring in f.as_posix())
    ]

    versioned_files = []
    for file in candidates:
        version_str = ""
        for char in reversed(file.stem):
            if char.isdigit():
                version_str = char + version_str
            else:
                break

        if version_str:
            versioned_files.append((file, int(version_str)))

    if versioned_files:
        return max(versioned_files, key=lambda x: x[1])[0]

    return None


def get_next_version_from_dir(
    filepath: Path, extension: str, substring: Optional[str] = None, padding: int = 3
) -> str:
    """
    Gets the next version number for versioned files in a directory.

    Args:
        filepath (Path): The directory to search.
        extension (str): The file extension to filter by (with or without
            leading dot).
        substring (str): Optional substring the filename must contain.
        padding (int): The number of digits for the version number (default: 3).

    Returns:
        str: The next version number as a zero-padded string (e.g., '004' if
            '003' exists).
        Returns '001' if no versioned files are found.

    Note:
        Assumes version number is the last N digits before the file extension.
        Example: "shot_v001.exr", "render_042.txt"
    """
    if not filepath or not filepath.exists():
        return "1".zfill(padding)

    ext = extension if extension.startswith(".") else f".{extension}"

    versioned_files = []
    for item in filepath.iterdir():
        if not item.is_file():
            continue
        if item.suffix != ext:
            continue
        if substring and substring not in item.name:
            continue

        if item.stem[-padding:].isdigit():
            version_num = int(item.stem[-padding:])
            versioned_files.append(version_num)

    if versioned_files:
        next_version = max(versioned_files) + 1
        return str(next_version).zfill(padding)

    return "1".zfill(padding)
