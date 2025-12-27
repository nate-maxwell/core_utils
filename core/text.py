import time
import shutil
import sys
from typing import Any
from typing import Optional
from typing import Sequence


def print_center_header(title: str, header_char: str = "-") -> None:
    """
    Prints a header line with the title, surrounded by spaces and a
    line of the header_char. Will dynamically size to the terminal width,
    if able, otherwise will default to width 80.

    Args:
        title (str): The header title, or what to put in the header.
        header_char (str): The character to make the header line.
            Defaults to '-'.
    """
    msg = title.strip()
    width, _ = shutil.get_terminal_size()
    print(f" {msg} ".center(width, header_char))


def _print_msg(header: str, msg: str, custom_tag: Optional[str] = None) -> None:
    """>>> [HEADER][TAG] - msg"""
    tag = custom_tag.upper() if custom_tag else ""
    if custom_tag and not custom_tag.startswith("["):
        tag = f"[{tag}]"
    print(f"[{header}]{tag} - {msg}")


def print_error_msg(msg: str, custom_tag: Optional[str] = None) -> None:
    """Simple print wrapper with [ERROR] header and timestamp."""
    _print_msg("ERROR", msg, custom_tag)


class ProgressBar(object):
    """
    A progress bar that outputs to stderr for tracking progress when looping.

    Example usages:
    >>> for _ in ProgressBar(range(11)):
    >>>     ...

    Args:
        data(sequence): Any sequence data type that can be looped through.
    """

    def __init__(self, data: Sequence[Any]):
        self.data = data
        self.index = 0
        self.start_time = time.perf_counter()
        self.last_time = self.start_time
        self.iteration_time = time.perf_counter()

    def __iter__(self) -> "ProgressBar":
        return self

    def __next__(self) -> Any:
        if self.index < len(self.data):
            result = self.data[self.index]
            self.index += 1

            current_time = time.perf_counter()
            self.iteration_time = current_time - self.last_time
            self.last_time = current_time

            self.draw_progress_bar()
            return result
        else:
            raise StopIteration

    def draw_progress_bar(self) -> None:
        """
        Outputs the progress bar to stderr, with percentage filled based on the
        current index of the sequence data item.
        Will flush stderr each time the progress bar is drawn.
        """
        percent = self.index / len(self.data)
        bar_len = 20
        sys.stderr.write("\r")
        progress = ""
        for i in range(bar_len):
            if i < int(bar_len * percent):
                progress += "█"
            else:
                progress += " "

        progress_bar_str = "|%s| %.2f%% - Iteration time: %.4f seconds"
        sys.stderr.write(
            progress_bar_str % (progress, percent * 100, self.iteration_time)
        )
        sys.stderr.flush()
