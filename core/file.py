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
