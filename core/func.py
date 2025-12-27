import functools
import time
from typing import Callable


def timer(func: Callable):
    """Decorator to print the time it takes to execute a function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        func(*args, **kwargs)
        print(f"Function took: {time.perf_counter() - start} seconds.")

    return wrapper


def print_func_name(func: Callable):
    """
    Decorator to print the name of the decorated function.
    If multiple decorators are used, place this one at the bottom of the
    decorator stack, else it will print the inner func from the previous
    decorator.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Func Name:: {func.__name__}")
        func(*args, **kwargs)

    return wrapper
