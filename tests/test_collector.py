import gc

import pytest

from core_utils.collector import freeze_gc


def test_freeze_gc_disables_gc_during_execution():
    """Test that GC is disabled during function execution."""
    gc_states = []

    @freeze_gc
    def check_gc_state():
        gc_states.append(gc.isenabled())

    gc.enable()
    check_gc_state()

    assert gc_states[0] is False


def test_freeze_gc_restores_enabled_state():
    """Test that GC is re-enabled after execution if it was enabled before."""
    gc.enable()
    initial_state = gc.isenabled()

    @freeze_gc
    def dummy_function():
        pass

    dummy_function()

    assert initial_state is True
    assert gc.isenabled() is True


def test_freeze_gc_preserves_disabled_state():
    """Test that GC remains disabled after execution if it was disabled before."""
    gc.disable()
    initial_state = gc.isenabled()

    @freeze_gc
    def dummy_function():
        pass

    dummy_function()

    assert initial_state is False
    assert gc.isenabled() is False


def test_freeze_gc_returns_function_result():
    """Test that the decorator preserves the function's return value."""

    @freeze_gc
    def return_value():
        return 42

    result = return_value()

    assert result == 42


def test_freeze_gc_passes_arguments():
    """Test that the decorator correctly passes arguments to the wrapped function."""

    @freeze_gc
    def add_numbers(a: int, b: int) -> int:
        return a + b

    result = add_numbers(5, 7)

    assert result == 12


def test_freeze_gc_passes_keyword_arguments():
    """Test that the decorator correctly passes keyword arguments."""

    @freeze_gc
    def greet(name: str, greeting: str = "Hello") -> str:
        return f"{greeting}, {name}!"

    result = greet(name="Alice", greeting="Hi")

    assert result == "Hi, Alice!"


def test_freeze_gc_restores_state_on_exception():
    """Test that GC is re-enabled after an exception if it was enabled before."""
    gc.enable()

    @freeze_gc
    def raise_error():
        raise ValueError("test error")

    with pytest.raises(ValueError, match="test error"):
        raise_error()

    assert gc.isenabled() is True


def test_freeze_gc_preserves_disabled_state_on_exception():
    """Test that GC remains disabled after an exception if it was disabled before."""
    gc.disable()

    @freeze_gc
    def raise_error():
        raise RuntimeError("test error")

    with pytest.raises(RuntimeError, match="test error"):
        raise_error()

    assert gc.isenabled() is False


def test_freeze_gc_preserves_function_metadata():
    """Test that the decorator preserves function metadata via @wraps."""

    @freeze_gc
    def documented_function():
        """This is a documented function."""
        pass

    assert documented_function.__name__ == "documented_function"
    assert documented_function.__doc__ == "This is a documented function."


def test_freeze_gc_with_multiple_calls():
    """Test that the decorator works correctly across multiple invocations."""
    gc.enable()

    @freeze_gc
    def counter(current: int) -> int:
        return current + 1

    result1 = counter(1)
    assert gc.isenabled() is True

    result2 = counter(2)
    assert gc.isenabled() is True

    assert result1 == 2
    assert result2 == 3
