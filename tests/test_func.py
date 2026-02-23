import gc
import time
import threading

import pytest

from core_utils import func


# -----timer Tests-------------------------------------------------------------


class TestTimer:
    def test_timer_decorator_prints_execution_time(self, capsys):
        @func.timer
        def sample_function():
            time.sleep(0.01)

        sample_function()
        captured = capsys.readouterr()

        assert "Function took:" in captured.out
        assert "seconds." in captured.out

    def test_timer_measures_actual_time(self, capsys):
        @func.timer
        def slow_function():
            time.sleep(0.1)

        slow_function()
        captured = capsys.readouterr()

        # Extract the time value from output
        time_str = captured.out.split("Function took: ")[1].split(" seconds")[0]
        elapsed_time = float(time_str)

        # Should be at least 0.1 seconds (with small tolerance)
        assert elapsed_time >= 0.09

    def test_timer_with_function_arguments(self, capsys):
        @func.timer
        def function_with_args(a, b, c=3):
            return a + b + c

        function_with_args(1, 2)
        captured = capsys.readouterr()

        assert "Function took:" in captured.out

    def test_timer_with_kwargs(self, capsys):
        @func.timer
        def function_with_kwargs(name, age=25):
            return f"{name} is {age}"

        function_with_kwargs("Alice", age=30)
        captured = capsys.readouterr()

        assert "Function took:" in captured.out

    def test_timer_preserves_function_name(self):
        @func.timer
        def my_function():
            pass

        assert my_function.__name__ == "my_function"

    def test_timer_preserves_function_docstring(self):
        @func.timer
        def documented_function():
            """This is a docstring."""
            pass

        assert documented_function.__doc__ == "This is a docstring."

    def test_timer_with_fast_function(self, capsys):
        @func.timer
        def instant_function():
            pass

        instant_function()
        captured = capsys.readouterr()

        # Should still print timing, even if very small
        assert "Function took:" in captured.out
        assert "seconds." in captured.out

    def test_timer_multiple_calls(self, capsys):
        @func.timer
        def repeated_function():
            time.sleep(0.01)

        repeated_function()
        repeated_function()
        captured = capsys.readouterr()

        # Should have two timing outputs
        assert captured.out.count("Function took:") == 2

    def test_timer_does_not_return_value(self):
        @func.timer
        def function_with_return():
            return 42

        result = function_with_return()

        # Timer decorator doesn't return the function's return value
        assert result is None


# -----print_func_name Tests---------------------------------------------------


class TestPrintFuncName:
    def test_print_func_name_prints_function_name(self, capsys):
        @func.print_func_name
        def sample_function():
            pass

        sample_function()
        captured = capsys.readouterr()

        assert "Func Name:: sample_function" in captured.out

    def test_print_func_name_with_arguments(self, capsys):
        @func.print_func_name
        def function_with_args(a, b):
            return a + b

        function_with_args(1, 2)
        captured = capsys.readouterr()

        assert "Func Name:: function_with_args" in captured.out

    def test_print_func_name_with_kwargs(self, capsys):
        # noinspection PyUnusedLocal
        @func.print_func_name
        def function_with_kwargs(name="test", value=10):
            pass

        function_with_kwargs(name="Alice", value=20)
        captured = capsys.readouterr()

        assert "Func Name:: function_with_kwargs" in captured.out

    def test_print_func_name_preserves_function_name(self):
        @func.print_func_name
        def my_function():
            pass

        assert my_function.__name__ == "my_function"

    def test_print_func_name_preserves_docstring(self):
        @func.print_func_name
        def documented_function():
            """This is a docstring."""
            pass

        assert documented_function.__doc__ == "This is a docstring."

    def test_print_func_name_multiple_calls(self, capsys):
        @func.print_func_name
        def repeated_function():
            pass

        repeated_function()
        repeated_function()
        repeated_function()
        captured = capsys.readouterr()

        # Should print name three times
        assert captured.out.count("Func Name::") == 3

    def test_print_func_name_does_not_return_value(self):
        @func.print_func_name
        def function_with_return():
            return 99

        result = function_with_return()

        # Decorator doesn't return the function's return value
        assert result is None


# -----Decorator Stacking Tests------------------------------------------------


class TestDecoratorStacking:
    def test_timer_and_print_func_name_stacked(self, capsys):
        @func.timer
        @func.print_func_name
        def stacked_function():
            time.sleep(0.01)

        stacked_function()
        captured = capsys.readouterr()

        # Both decorators should print
        assert "Func Name:: stacked_function" in captured.out
        assert "Function took:" in captured.out

    def test_print_func_name_bottom_of_stack(self, capsys):
        @func.timer
        @func.print_func_name
        def correct_order():
            pass

        correct_order()
        captured = capsys.readouterr()

        # print_func_name at bottom should print correct name
        assert "Func Name:: correct_order" in captured.out

    def test_print_func_name_top_of_stack_shows_wrapper(self, capsys):
        @func.print_func_name
        @func.timer
        def wrong_order():
            pass

        wrong_order()
        captured = capsys.readouterr()

        # print_func_name at top would print 'wrapper' due to functools.wraps
        # Actually, with functools.wraps it should still preserve the name
        assert "Func Name:: wrong_order" in captured.out

    def test_multiple_timer_decorators(self, capsys):
        @func.timer
        @func.timer
        def double_timed():
            time.sleep(0.01)

        double_timed()
        captured = capsys.readouterr()

        # Should have two timing outputs (outer and inner)
        assert captured.out.count("Function took:") == 2


# -----GC Freeze Decorator-----------------------------------------------------


def test_freeze_gc_disables_gc_during_execution():
    """Test that GC is disabled during function execution."""
    gc_states = []

    @func.freeze_gc
    def check_gc_state():
        gc_states.append(gc.isenabled())

    gc.enable()
    check_gc_state()

    assert gc_states[0] is False


def test_freeze_gc_restores_enabled_state():
    """Test that GC is re-enabled after execution if it was enabled before."""
    gc.enable()
    initial_state = gc.isenabled()

    @func.freeze_gc
    def dummy_function():
        pass

    dummy_function()

    assert initial_state is True
    assert gc.isenabled() is True


def test_freeze_gc_preserves_disabled_state():
    """Test that GC remains disabled after execution if it was disabled before."""
    gc.disable()
    initial_state = gc.isenabled()

    @func.freeze_gc
    def dummy_function():
        pass

    dummy_function()

    assert initial_state is False
    assert gc.isenabled() is False


def test_freeze_gc_returns_function_result():
    """Test that the decorator preserves the function's return value."""

    @func.freeze_gc
    def return_value():
        return 42

    result = return_value()

    assert result == 42


def test_freeze_gc_passes_arguments():
    """Test that the decorator correctly passes arguments to the wrapped function."""

    @func.freeze_gc
    def add_numbers(a: int, b: int) -> int:
        return a + b

    result = add_numbers(5, 7)

    assert result == 12


def test_freeze_gc_passes_keyword_arguments():
    """Test that the decorator correctly passes keyword arguments."""

    @func.freeze_gc
    def greet(name: str, greeting: str = "Hello") -> str:
        return f"{greeting}, {name}!"

    result = greet(name="Alice", greeting="Hi")

    assert result == "Hi, Alice!"


def test_freeze_gc_restores_state_on_exception():
    """Test that GC is re-enabled after an exception if it was enabled before."""
    gc.enable()

    @func.freeze_gc
    def raise_error():
        raise ValueError("test error")

    with pytest.raises(ValueError, match="test error"):
        raise_error()

    assert gc.isenabled() is True


def test_freeze_gc_preserves_disabled_state_on_exception():
    """Test that GC remains disabled after an exception if it was disabled before."""
    gc.disable()

    @func.freeze_gc
    def raise_error():
        raise RuntimeError("test error")

    with pytest.raises(RuntimeError, match="test error"):
        raise_error()

    assert gc.isenabled() is False


def test_freeze_gc_preserves_function_metadata():
    """Test that the decorator preserves function metadata via @wraps."""

    @func.freeze_gc
    def documented_function():
        """This is a documented function."""
        pass

    assert documented_function.__name__ == "documented_function"
    assert documented_function.__doc__ == "This is a documented function."


def test_freeze_gc_with_multiple_calls():
    """Test that the decorator works correctly across multiple invocations."""
    gc.enable()

    @func.freeze_gc
    def counter(current: int) -> int:
        return current + 1

    result1 = counter(1)
    assert gc.isenabled() is True

    result2 = counter(2)
    assert gc.isenabled() is True

    assert result1 == 2
    assert result2 == 3


# -----Edge Cases--------------------------------------------------------------


class TestEdgeCases:
    def test_timer_with_exception(self, capsys):
        @func.timer
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        # Timer might not complete if exception is raised
        # This tests current behavior

    def test_print_func_name_with_exception(self, capsys):
        @func.print_func_name
        def failing_function():
            raise RuntimeError("Test error")

        with pytest.raises(RuntimeError):
            failing_function()

        captured = capsys.readouterr()
        # Function name should still be printed before exception
        assert "Func Name:: failing_function" in captured.out

    def test_decorators_with_empty_function(self, capsys):
        @func.timer
        @func.print_func_name
        def empty_function():
            pass

        empty_function()
        captured = capsys.readouterr()

        assert "Func Name:: empty_function" in captured.out
        assert "Function took:" in captured.out

    def test_timer_with_lambda_function(self, capsys):
        # Lambdas can be decorated too
        timed_lambda = func.timer(lambda x: x * 2)
        timed_lambda(5)
        captured = capsys.readouterr()

        assert "Function took:" in captured.out


# -----Once Tests--------------------------------------------------------------


class TestOnce:
    def test_runs_exactly_once(self) -> None:
        call_count = [0]

        @func.once
        def fn() -> None:
            call_count[0] += 1

        fn()
        fn()
        fn()
        assert call_count[0] == 1

    def test_subsequent_calls_are_silently_ignored(self) -> None:
        log = []

        @func.once
        def fn() -> None:
            log.append("ran")

        for _ in range(10):
            fn()
        assert log == ["ran"]

    def test_return_value_is_always_none(self) -> None:
        @func.once
        def fn() -> None:
            return 42  # type: ignore[return-value]

        assert fn() is None
        assert fn() is None

    def test_preserves_function_name(self) -> None:
        @func.once
        def my_setup_func() -> None:
            pass

        assert my_setup_func.__name__ == "my_setup_func"

    def test_preserves_docstring(self) -> None:
        @func.once
        def my_setup_func() -> None:
            """Registers all pipeline plugins."""
            pass

        assert my_setup_func.__doc__ == "Registers all pipeline plugins."

    def test_each_decorated_function_is_independent(self) -> None:
        counts = [0, 0]

        @func.once
        def fn_a() -> None:
            counts[0] += 1

        @func.once
        def fn_b() -> None:
            counts[1] += 1

        fn_a()
        fn_a()
        fn_b()
        fn_b()
        fn_b()
        assert counts == [1, 1]

    def test_does_not_run_before_first_call(self) -> None:
        ran = [False]

        @func.once
        def fn() -> None:
            ran[0] = True

        assert ran[0] is False
        fn()
        assert ran[0] is True


class TestOnceExceptions:
    def test_exception_propagates_to_caller(self) -> None:
        @func.once
        def fn() -> None:
            raise ValueError("setup failed")

        with pytest.raises(ValueError, match="setup failed"):
            fn()

    def test_does_not_run_again_after_exception(self) -> None:
        """Once the function raises, subsequent calls are still ignored.
        This is intentional: if setup is broken, calling it again won't fix it,
        and silently swallowing repeated failures is safer than retrying
        indefinitely in a pipeline context.
        """
        call_count = [0]

        @func.once
        def fn() -> None:
            call_count[0] += 1
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError):
            fn()

        fn()  # should be ignored
        fn()  # should be ignored
        assert call_count[0] == 1


class TestOnceThreadSafety:
    def test_only_runs_once_under_concurrent_calls(self) -> None:
        call_count = [0]
        n_threads = 50
        barrier = threading.Barrier(n_threads)

        @func.once
        def fn() -> None:
            call_count[0] += 1

        def task() -> None:
            barrier.wait()  # all threads start simultaneously
            fn()

        threads = [threading.Thread(target=task) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert call_count[0] == 1

    def test_side_effect_is_visible_to_all_threads(self) -> None:
        shared_state = {}
        n_threads = 20
        barrier = threading.Barrier(n_threads)

        @func.once
        def fn() -> None:
            shared_state["ready"] = True

        def task() -> None:
            barrier.wait()
            fn()

        threads = [threading.Thread(target=task) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert shared_state.get("ready") is True
