import functools
import gc
import threading
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


def once(func: Callable) -> Callable:
    """
    Decorator that ensures a function executes at most once, regardless of
    how many times it is called. All calls return the value from the first
    execution. Thread-safe.

    Useful for one-time setup that must not repeat: registering plugins,
    configuring a logger, seeding a random state, etc.

    If the first call raises, the exception propagates and the function will
    not run again on subsequent calls — they will return None instead.

    Example:
        @once
        def register_plugins() -> None:
            ...

        register_plugins()  # runs
        register_plugins()  # silently ignored
        register_plugins()  # silently ignored
    """
    lock = threading.Lock()
    has_run = False
    result = None

    def wrapper(*args, **kwargs) -> Any:
        nonlocal has_run, result
        if has_run:
            return result
        with lock:
            if has_run:
                return result
            has_run = True
            result = func(*args, **kwargs)
            return result

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper
