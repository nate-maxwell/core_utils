import os
from pathlib import Path

import pytest

from core_utils import env


# Prefix all test keys to avoid collisions with real environment variables.
_PREFIX = "TEST_ENV_"


@pytest.fixture(autouse=True)
def clean_env():
    """Remove all test-prefixed keys before and after each test."""
    _purge()
    yield
    _purge()


def _purge() -> None:
    for key in list(os.environ):
        if key.startswith(_PREFIX):
            del os.environ[key]


def _key(name: str) -> str:
    return f"{_PREFIX}{name}"


# -----get_str-----------------------------------------------------------------


class TestGetStr:
    def test_returns_value_when_set(self) -> None:
        os.environ[_key("STR")] = "hello"
        assert env.get_str(_key("STR")) == "hello"

    def test_returns_none_when_missing(self) -> None:
        assert env.get_str(_key("MISSING")) is None

    def test_returns_fallback_when_missing(self) -> None:
        assert env.get_str(_key("MISSING"), fallback="default") == "default"

    def test_empty_string_is_returned_as_is(self) -> None:
        os.environ[_key("STR")] = ""
        assert env.get_str(_key("STR")) == ""


# -----get_int-----------------------------------------------------------------


class TestGetInt:
    def test_returns_int_when_set(self) -> None:
        os.environ[_key("INT")] = "42"
        assert env.get_int(_key("INT")) == 42

    def test_returns_none_when_missing(self) -> None:
        assert env.get_int(_key("MISSING")) is None

    def test_returns_fallback_when_missing(self) -> None:
        assert env.get_int(_key("MISSING"), fallback=0) == 0

    def test_returns_fallback_on_invalid_value(self) -> None:
        os.environ[_key("INT")] = "not_a_number"
        assert env.get_int(_key("INT"), fallback=-1) == -1

    def test_returns_none_on_invalid_value_with_no_fallback(self) -> None:
        os.environ[_key("INT")] = "not_a_number"
        assert env.get_int(_key("INT")) is None

    def test_negative_integer(self) -> None:
        os.environ[_key("INT")] = "-10"
        assert env.get_int(_key("INT")) == -10

    def test_zero(self) -> None:
        os.environ[_key("INT")] = "0"
        assert env.get_int(_key("INT")) == 0


# -----get_bool----------------------------------------------------------------


class TestGetBool:
    @pytest.mark.parametrize(
        "value", ["1", "true", "True", "TRUE", "yes", "YES", "on", "ON"]
    )
    def test_truthy_values(self, value: str) -> None:
        os.environ[_key("BOOL")] = value
        assert env.get_bool(_key("BOOL")) is True

    @pytest.mark.parametrize(
        "value", ["0", "false", "False", "FALSE", "no", "NO", "off", "OFF"]
    )
    def test_falsy_values(self, value: str) -> None:
        os.environ[_key("BOOL")] = value
        assert env.get_bool(_key("BOOL")) is False

    def test_returns_none_when_missing(self) -> None:
        assert env.get_bool(_key("MISSING")) is None

    def test_returns_fallback_when_missing(self) -> None:
        assert env.get_bool(_key("MISSING"), fallback=True) is True

    def test_returns_fallback_on_unrecognised_value(self) -> None:
        os.environ[_key("BOOL")] = "maybe"
        assert env.get_bool(_key("BOOL"), fallback=False) is False

    def test_returns_none_on_unrecognised_value_with_no_fallback(self) -> None:
        os.environ[_key("BOOL")] = "maybe"
        assert env.get_bool(_key("BOOL")) is None


# -----get_path----------------------------------------------------------------


class TestGetPath:
    def test_returns_path_when_set(self, tmp_path: Path) -> None:
        os.environ[_key("PATH")] = str(tmp_path)
        result = env.get_path(_key("PATH"))
        assert isinstance(result, Path)
        assert result == tmp_path.resolve()

    def test_returns_none_when_missing(self) -> None:
        assert env.get_path(_key("MISSING")) is None

    def test_returns_fallback_when_missing(self, tmp_path: Path) -> None:
        result = env.get_path(_key("MISSING"), fallback=tmp_path)
        assert result == tmp_path

    def test_path_is_resolved(self) -> None:
        os.environ[_key("PATH")] = "/some/../some/path"
        result = env.get_path(_key("PATH"))
        assert ".." not in result.parts


# -----get_list----------------------------------------------------------------


class TestGetList:
    def test_splits_on_default_delimiter(self) -> None:
        os.environ[_key("LIST")] = os.pathsep.join(["maya", "nuke", "houdini"])
        assert env.get_list(_key("LIST")) == ["maya", "nuke", "houdini"]

    def test_custom_delimiter(self) -> None:
        os.environ[_key("LIST")] = "maya;nuke;houdini"
        assert env.get_list(_key("LIST"), delimiter=";") == ["maya", "nuke", "houdini"]

    def test_returns_none_when_missing(self) -> None:
        assert env.get_list(_key("MISSING")) is None

    def test_returns_fallback_when_missing(self) -> None:
        assert env.get_list(_key("MISSING"), fallback=[]) == []

    def test_empty_segments_are_dropped(self) -> None:
        os.environ[_key("LIST")] = "maya,,nuke"
        assert env.get_list(_key("LIST"), delimiter=",") == ["maya", "nuke"]

    def test_single_item(self) -> None:
        os.environ[_key("LIST")] = "maya"
        assert env.get_list(_key("LIST"), delimiter=",") == ["maya"]


# -----require-----------------------------------------------------------------


class TestRequire:
    def test_passes_when_all_vars_set(self) -> None:
        os.environ[_key("A")] = "1"
        os.environ[_key("B")] = "2"
        env.require([_key("A"), _key("B")])  # should not raise

    def test_raises_when_one_missing(self) -> None:
        os.environ[_key("A")] = "1"
        with pytest.raises(EnvironmentError, match=_key("B")):
            env.require([_key("A"), _key("B")])

    def test_raises_with_all_missing_vars_in_message(self) -> None:
        with pytest.raises(EnvironmentError) as exc_info:
            env.require([_key("X"), _key("Y"), _key("Z")])
        message = str(exc_info.value)
        assert _key("X") in message
        assert _key("Y") in message
        assert _key("Z") in message

    def test_raises_when_var_is_empty_string(self) -> None:
        os.environ[_key("A")] = ""
        with pytest.raises(EnvironmentError, match=_key("A")):
            env.require([_key("A")])

    def test_empty_key_list_does_not_raise(self) -> None:
        env.require([])  # should not raise


# -----load_env_file-----------------------------------------------------------


class TestLoadEnvFile:
    def test_basic_key_value(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("TESTKEY=hello\n")
        env.load_env_file(f, overwrite=True)
        assert os.environ["TESTKEY"] == "hello"
        del os.environ["TESTKEY"]

    def test_double_quoted_value(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text(f'{_key("Q")}="quoted value"\n')
        env.load_env_file(f, overwrite=True)
        assert os.environ[_key("Q")] == "quoted value"

    def test_single_quoted_value(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text(f"{_key('Q')}='quoted value'\n")
        env.load_env_file(f, overwrite=True)
        assert os.environ[_key("Q")] == "quoted value"

    def test_inline_comment_stripped(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text(f"{_key('C')}=value  # this is a comment\n")
        env.load_env_file(f, overwrite=True)
        assert os.environ[_key("C")] == "value"

    def test_full_line_comment_ignored(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text(f"# this whole line is a comment\n{_key('D')}=present\n")
        env.load_env_file(f, overwrite=True)
        assert os.environ[_key("D")] == "present"

    def test_blank_lines_ignored(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text(f"\n\n{_key('E')}=value\n\n")
        env.load_env_file(f, overwrite=True)
        assert os.environ[_key("E")] == "value"

    def test_overwrite_false_does_not_replace_existing(self, tmp_path: Path) -> None:
        os.environ[_key("F")] = "original"
        f = tmp_path / ".env"
        f.write_text(f"{_key('F')}=new_value\n")
        env.load_env_file(f, overwrite=False)
        assert os.environ[_key("F")] == "original"

    def test_overwrite_true_replaces_existing(self, tmp_path: Path) -> None:
        os.environ[_key("G")] = "original"
        f = tmp_path / ".env"
        f.write_text(f"{_key('G')}=new_value\n")
        env.load_env_file(f, overwrite=True)
        assert os.environ[_key("G")] == "new_value"

    def test_returns_loaded_pairs(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text(f"{_key('H')}=one\n{_key('I')}=two\n")
        env.load_env_file(f, overwrite=True)
        assert os.environ[_key("H")] == "one"
        assert os.environ[_key("I")] == "two"

    def test_raises_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            env.load_env_file(tmp_path / "nonexistent.env")

    def test_line_without_equals_is_skipped(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text(f"NOTAVALIDLINE\n{_key('J')}=valid\n")
        env.load_env_file(f, overwrite=True)
        assert "NOTAVALIDLINE" not in os.environ
        assert os.environ[_key("J")] == "valid"
