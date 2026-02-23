import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def run_detached(
    cmd: list[str],
    cwd: Optional[Path] = None,
    env: Optional[dict[str, str]] = None,
) -> subprocess.Popen:
    """
    Launch a process in a detached, fire-and-forget manner.
    The child process is fully independent: it will not be killed if the
    parent exits, and its stdout/stderr are discarded.
    Useful for launching DCCs or other long-running tools from a pipeline
    script that should not block.

    Args:
        cmd (list[str]): The command and its arguments.
        cwd (Path): Working directory to run the command in. Defaults to None.
        env (dict[str, str]): Extra environment variables to merge into the
            current environment. Defaults to None.
    Returns:
        subprocess.Popen: The process handle. Its PID is available as .pid.
    """
    merged_env = {**os.environ}
    if env:
        merged_env.update(env)

    kwargs: dict = dict(
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=cwd,
        env=merged_env,
    )

    if sys.platform == "win32":
        kwargs["creationflags"] = (
            subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        kwargs["start_new_session"] = True

    return subprocess.Popen(cmd, **kwargs)


def which(executable: str) -> Optional[Path]:
    """
    Locate an executable on PATH, returning its full path.
    A typed, Path-returning wrapper around shutil.which.

    Args:
        executable (str): The executable name to find (e.g. 'python', 'ffmpeg').
    Returns:
        Optional[Path]: The full path to the executable, or None if not found.
    """
    result = shutil.which(executable)
    return Path(result) if result else None
