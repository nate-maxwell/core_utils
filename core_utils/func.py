import functools
import gc
import time
from functools import wraps
from typing import Any
from typing import Callable


def timer(func: Callable) -> Callable:
    """Decorator to print the time it takes to execute a function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        func(*args, **kwargs)
        print(f"Function took: {time.perf_counter() - start} seconds.")

    return wrapper


def print_func_name(func: Callable) -> Callable:
    """
    Decorator to print the name of the decorated function.
    If multiple decorators are used, place this one at the bottom of the
    decorator stack, else it will print the inner func from the previous
    decorator.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        print(f"Func Name:: {func.__name__}")
        func(*args, **kwargs)

    return wrapper


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
