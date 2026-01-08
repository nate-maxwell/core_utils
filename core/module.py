import inspect
import sys


def prevent_reimport() -> None:
    """
    Prevents a module from being reimported/reloaded.
    Call this at the top of any module you want to protect.
    """
    # Get the caller's frame to find which module called us
    frame = inspect.currentframe().f_back
    module_name = frame.f_globals["__name__"]

    if module_name in sys.modules:
        existing = sys.modules[module_name]
        if hasattr(existing, "_IMPORT_GUARD"):
            raise ImportError(
                f"Module '{module_name}' has already been imported and cannot be reloaded. "
                f"Restart your Python session to reimport this module."
            )

    frame.f_globals["_IMPORT_GUARD"] = True
