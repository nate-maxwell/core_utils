import gc
from functools import wraps
from typing import Any
from typing import Callable


def freeze_gc(func: Callable) -> Callable:
    """
    Decorator that freezes the garbage collector for the duration of the function.
    Ensures GC is unfrozen even if an exception occurs.

    Examples:
        @freeze_gc
        def performance_critical_function():
            # Your code here
            data = [i for i in range(1000000)]
            return sum(data)

        @freeze_gc
        def possible_erroring_function():
            raise ValueError('wrong value')
    """

    @wraps(func)
    def wrapper(*args: tuple[Any], **kwargs: dict[str, Any]) -> Any:
        was_enabled = gc.isenabled()
        gc.disable()

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            if was_enabled:
                gc.enable()

    return wrapper
