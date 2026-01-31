import time
from io import StringIO
from unittest.mock import patch

import pytest

from core_utils import text


# -----print_center_header Tests-----------------------------------------------


class TestPrintCenterHeader:
    def test_print_center_header_default_char(self, capsys):
        text.print_center_header("Test Header")
        captured = capsys.readouterr()
        assert "Test Header" in captured.out
        assert "-" in captured.out

    def test_print_center_header_custom_char(self, capsys):
        text.print_center_header("Test Header", "=")
        captured = capsys.readouterr()
        assert "Test Header" in captured.out
        assert "=" in captured.out
        assert "-" not in captured.out

    def test_print_center_header_strips_whitespace(self, capsys):
        text.print_center_header("  Test Header  ")
        captured = capsys.readouterr()
        assert " Test Header " in captured.out

    @patch("shutil.get_terminal_size")
    def test_print_center_header_respects_terminal_width(
        self, mock_terminal_size, capsys
    ):
        mock_terminal_size.return_value = (40, 24)
        text.print_center_header("Test")
        captured = capsys.readouterr()
        # Should be centered in 40 character width
        assert len(captured.out.strip()) == 40

    def test_print_center_header_empty_string(self, capsys):
        text.print_center_header("")
        captured = capsys.readouterr()
        assert captured.out.strip()  # Should still output something


# -----print_error_msg Tests---------------------------------------------------


class TestPrintErrorMsg:
    def test_print_error_msg_basic(self, capsys):
        text.print_error_msg("Something went wrong")
        captured = capsys.readouterr()
        assert "[ERROR]" in captured.out
        assert "Something went wrong" in captured.out

    def test_print_error_msg_with_custom_tag(self, capsys):
        text.print_error_msg("File not found", "FILE")
        captured = capsys.readouterr()
        assert "[ERROR]" in captured.out
        assert "[FILE]" in captured.out
        assert "File not found" in captured.out

    def test_print_error_msg_with_custom_tag_already_bracketed(self, capsys):
        text.print_error_msg("Connection failed", "[NETWORK]")
        captured = capsys.readouterr()
        assert "[ERROR]" in captured.out
        assert "[NETWORK]" in captured.out
        assert "Connection failed" in captured.out

    def test_print_error_msg_custom_tag_uppercase(self, capsys):
        text.print_error_msg("Error occurred", "database")
        captured = capsys.readouterr()
        assert "[DATABASE]" in captured.out


# -----ProgressBar Tests-------------------------------------------------------


class TestProgressBar:
    @pytest.fixture
    def sample_data(self):
        return [1, 2, 3, 4, 5]

    def test_progress_bar_initialization(self, sample_data):
        pb = text.ProgressBar(sample_data)
        assert pb.data == sample_data
        assert pb.index == 0
        assert pb.start_time > 0

    def test_progress_bar_iteration(self, sample_data):
        pb = text.ProgressBar(sample_data)
        results = []
        for item in pb:
            results.append(item)
        assert results == sample_data

    def test_progress_bar_iter_returns_self(self, sample_data):
        pb = text.ProgressBar(sample_data)
        assert pb.__iter__() is pb

    def test_progress_bar_raises_stop_iteration(self, sample_data):
        pb = text.ProgressBar(sample_data)
        # Consume all items
        for _ in pb:
            pass
        # Next call should raise StopIteration
        with pytest.raises(StopIteration):
            next(pb)

    def test_progress_bar_index_increments(self, sample_data):
        pb = text.ProgressBar(sample_data)
        assert pb.index == 0
        next(pb)
        assert pb.index == 1
        next(pb)
        assert pb.index == 2

    def test_progress_bar_tracks_iteration_time(self, sample_data):
        pb = text.ProgressBar(sample_data)
        next(pb)
        assert pb.iteration_time >= 0
        time.sleep(0.01)
        next(pb)
        assert pb.iteration_time > 0

    def test_progress_bar_outputs_to_stderr(self, sample_data):
        pb = text.ProgressBar(sample_data)
        stderr_capture = StringIO()

        with patch("sys.stderr", stderr_capture):
            next(pb)

        output = stderr_capture.getvalue()
        assert "|" in output
        assert "%" in output
        assert "Iteration time" in output

    def test_progress_bar_percentage_calculation(self, sample_data):
        pb = text.ProgressBar(sample_data)
        stderr_capture = StringIO()

        with patch("sys.stderr", stderr_capture):
            next(pb)  # First item (20%)

        output = stderr_capture.getvalue()
        assert "20.00%" in output

    def test_progress_bar_with_empty_sequence(self):
        pb = text.ProgressBar([])
        with pytest.raises(StopIteration):
            next(pb)

    def test_progress_bar_with_single_item(self):
        pb = text.ProgressBar([42])
        stderr_capture = StringIO()

        with patch("sys.stderr", stderr_capture):
            result = next(pb)

        assert result == 42
        output = stderr_capture.getvalue()
        assert "100.00%" in output

    def test_progress_bar_full_iteration_with_stderr(self, sample_data):
        pb = text.ProgressBar(sample_data)
        stderr_capture = StringIO()
        results = []

        with patch("sys.stderr", stderr_capture):
            for item in pb:
                results.append(item)

        assert results == sample_data
        output = stderr_capture.getvalue()
        # Should have progress bar characters
        assert "█" in output or " " in output
        assert "100.00%" in output

    def test_progress_bar_with_range(self):
        pb = text.ProgressBar(range(10))
        results = []
        for item in pb:
            results.append(item)
        assert results == list(range(10))

    def test_progress_bar_draw_progress_bar_format(self, sample_data):
        pb = text.ProgressBar(sample_data)
        pb.index = 3  # Set to 60%
        stderr_capture = StringIO()

        with patch("sys.stderr", stderr_capture):
            pb.draw_progress_bar()

        output = stderr_capture.getvalue()
        assert "60.00%" in output
        assert "Iteration time:" in output
        assert "seconds" in output

    def test_progress_bar_carriage_return_for_overwrite(self, sample_data):
        pb = text.ProgressBar(sample_data)
        stderr_capture = StringIO()

        with patch("sys.stderr", stderr_capture):
            next(pb)

        output = stderr_capture.getvalue()
        assert output.startswith("\r")
