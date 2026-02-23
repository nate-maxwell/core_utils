import os
import sys
from pathlib import Path

from core_utils import proc

# -----helpers-----------------------------------------------------------------


def _noop_cmd() -> list[str]:
    """A cross-platform command that exits immediately with code 0."""
    if sys.platform == "win32":
        return ["cmd", "/c", "exit", "0"]
    return ["true"]


def _write_env_var_cmd(var: str, out: Path) -> list[str]:
    """A command that writes the value of an env var to a file."""
    if sys.platform == "win32":
        return ["cmd", "/c", f"echo %{var}% > {out}"]
    return ["sh", "-c", f'echo "${var}" > "{out}"']


def _write_cwd_cmd(out: Path) -> list[str]:
    """A command that writes the current working directory to a file."""
    if sys.platform == "win32":
        return ["cmd", "/c", f"cd > {out}"]
    return ["sh", "-c", f'pwd > "{out}"']


# -----which-------------------------------------------------------------------


class TestWhich:
    def test_returns_path_for_known_executable(self) -> None:
        # python is always on PATH in a venv
        result = proc.which("python")
        assert result is not None
        assert isinstance(result, Path)

    def test_returns_none_for_unknown_executable(self) -> None:
        result = proc.which("this_executable_does_not_exist_xyz")
        assert result is None

    def test_returned_path_exists(self) -> None:
        result = proc.which("python")
        assert result is not None
        assert result.exists()

    def test_returned_path_is_absolute(self) -> None:
        result = proc.which("python")
        assert result is not None
        assert result.is_absolute()


# -----run_detached------------------------------------------------------------


class TestRunDetached:
    def test_returns_popen_instance(self) -> None:
        import subprocess

        cmd = _noop_cmd()
        proc_ = proc.run_detached(cmd)
        proc_.wait(timeout=5)
        assert isinstance(proc_, subprocess.Popen)

    def test_process_has_pid(self) -> None:
        cmd = _noop_cmd()
        proc_ = proc.run_detached(cmd)
        proc_.wait(timeout=5)
        assert isinstance(proc_.pid, int)
        assert proc_.pid > 0

    def test_process_runs_successfully(self) -> None:
        cmd = _noop_cmd()
        proc_ = proc.run_detached(cmd)
        returncode = proc_.wait(timeout=5)
        assert returncode == 0

    def test_extra_env_vars_are_passed(self, tmp_path: Path) -> None:
        # Write the env var value to a temp file so we can inspect it
        # from the detached child without stdout.
        out = tmp_path / "out.txt"
        cmd = _write_env_var_cmd("TEST_PROC_CANARY", out)
        proc_ = proc.run_detached(cmd, env={"TEST_PROC_CANARY": "hello"})
        proc_.wait(timeout=5)
        assert out.read_text().strip() == "hello"

    def test_extra_env_does_not_discard_existing_env(self, tmp_path: Path) -> None:
        # PATH must survive the merge or the child cannot find anything.
        out = tmp_path / "out.txt"
        cmd = _write_env_var_cmd("PATH", out)
        proc_ = proc.run_detached(cmd, env={"EXTRA": "value"})
        proc_.wait(timeout=5)
        assert out.read_text().strip() != ""

    def test_cwd_is_respected(self, tmp_path: Path) -> None:
        out = tmp_path / "out.txt"
        cmd = _write_cwd_cmd(out)
        proc_ = proc.run_detached(cmd, cwd=tmp_path)
        proc_.wait(timeout=5)
        written = Path(out.read_text().strip())
        assert written.resolve() == tmp_path.resolve()

    def test_no_env_arg_inherits_environment(self, tmp_path: Path) -> None:
        os.environ["TEST_PROC_INHERIT"] = "inherited"
        out = tmp_path / "out.txt"
        cmd = _write_env_var_cmd("TEST_PROC_INHERIT", out)
        proc_ = proc.run_detached(cmd)
        proc_.wait(timeout=5)
        assert out.read_text().strip() == "inherited"
        del os.environ["TEST_PROC_INHERIT"]
