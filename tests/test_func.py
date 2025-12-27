import time

import pytest

from core import func


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
