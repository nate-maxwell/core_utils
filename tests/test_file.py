from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from core_utils import filesys


class TestCanCreatePathIterative(object):
    """Unit tests for can_create_path_iterative function."""

    def test_valid_path_in_writable_directory(self) -> None:
        """Test that a valid path in a writable directory returns True."""
        with TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir) / "subdir" / "nested" / "file.txt"
            assert filesys.can_create_path(test_path) is True

    def test_invalid_characters_return_false(self) -> None:
        """Test that paths with invalid Windows characters return False."""
        invalid_chars = ["<", ">", "|", "?", "*", '"']

        for char in invalid_chars:
            test_path = Path(f"C:/valid/path{char}invalid/file.txt")
            assert filesys.can_create_path(test_path) is False

    def test_reserved_names_return_false(self) -> None:
        """Test that Windows reserved names return False."""
        reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1", "con.txt"]

        with TemporaryDirectory() as tmpdir:
            for name in reserved_names:
                test_path = Path(tmpdir) / name
                assert filesys.can_create_path(test_path) is False

    def test_no_write_permission_returns_false(self) -> None:
        """Test that paths without write permission return False."""
        with TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir) / "subdir" / "file.txt"

            with patch("os.access", return_value=False):
                assert filesys.can_create_path(test_path) is False


class TestCreateStructure:
    def test_create_structure_simple(self, tmp_path, capsys):
        structure = {"folder1": {}, "folder2": {}}

        filesys.create_structure(structure, tmp_path)

        assert (tmp_path / "folder1").exists()
        assert (tmp_path / "folder1").is_dir()
        assert (tmp_path / "folder2").exists()
        assert (tmp_path / "folder2").is_dir()

        captured = capsys.readouterr()
        assert "written to" in captured.out

    def test_create_structure_nested(self, tmp_path):
        structure = {"assets": {"model": {}, "texture": {}, "anim": {}}, "config": {}}

        filesys.create_structure(structure, tmp_path)

        assert (tmp_path / "assets").exists()
        assert (tmp_path / "assets" / "model").exists()
        assert (tmp_path / "assets" / "texture").exists()
        assert (tmp_path / "assets" / "anim").exists()
        assert (tmp_path / "config").exists()

    def test_create_structure_deeply_nested(self, tmp_path):
        structure = {"level1": {"level2": {"level3": {"level4": {}}}}}

        filesys.create_structure(structure, tmp_path)

        assert (tmp_path / "level1" / "level2" / "level3" / "level4").exists()

    def test_create_structure_empty_dict(self, tmp_path):
        structure = {}

        filesys.create_structure(structure, tmp_path)

        # tmp_path should still exist
        assert tmp_path.exists()

    def test_create_structure_single_folder(self, tmp_path):
        structure = {"single": {}}

        filesys.create_structure(structure, tmp_path)

        assert (tmp_path / "single").exists()

    def test_create_structure_multiple_levels(self, tmp_path):
        structure = {
            "src": {"main": {}, "test": {}},
            "docs": {},
            "build": {"output": {}},
        }

        filesys.create_structure(structure, tmp_path)

        assert (tmp_path / "src" / "main").exists()
        assert (tmp_path / "src" / "test").exists()
        assert (tmp_path / "docs").exists()
        assert (tmp_path / "build" / "output").exists()

    def test_create_structure_prints_confirmation(self, tmp_path, capsys):
        structure = {"test": {}}

        filesys.create_structure(structure, tmp_path)

        captured = capsys.readouterr()
        assert str(structure) in captured.out
        assert str(tmp_path) in captured.out

    def test_create_structure_in_nonexistent_destination(self, tmp_path):
        destination = tmp_path / "new" / "nested" / "path"
        structure = {"folder": {}}

        filesys.create_structure(structure, destination)

        assert destination.exists()
        assert (destination / "folder").exists()


class TestSortPathList:
    def test_sort_path_list_alphabetical(self):
        paths = [Path("zebra.txt"), Path("alpha.txt"), Path("beta.txt")]

        result = filesys.sort_path_list(paths)

        assert result[0] == Path("alpha.txt")
        assert result[1] == Path("beta.txt")
        assert result[2] == Path("zebra.txt")

    def test_sort_path_list_numerical(self):
        paths = [Path("file10.txt"), Path("file2.txt"), Path("file1.txt")]

        result = filesys.sort_path_list(paths)

        assert result[0] == Path("file1.txt")
        assert result[1] == Path("file2.txt")
        assert result[2] == Path("file10.txt")

    def test_sort_path_list_mixed_alpha_numeric(self):
        paths = [
            Path("test100.txt"),
            Path("test20.txt"),
            Path("test3.txt"),
            Path("alpha.txt"),
        ]

        result = filesys.sort_path_list(paths)

        assert result[0] == Path("alpha.txt")
        assert result[1] == Path("test3.txt")
        assert result[2] == Path("test20.txt")
        assert result[3] == Path("test100.txt")

    def test_sort_path_list_with_directories(self):
        paths = [
            Path("folder/file10.txt"),
            Path("folder/file2.txt"),
            Path("folder/file1.txt"),
        ]

        result = filesys.sort_path_list(paths)

        assert result[0] == Path("folder/file1.txt")
        assert result[1] == Path("folder/file2.txt")
        assert result[2] == Path("folder/file10.txt")

    def test_sort_path_list_single_item(self):
        paths = [Path("single.txt")]

        result = filesys.sort_path_list(paths)

        assert result == paths

    def test_sort_path_list_none_input(self):
        result = filesys.sort_path_list(None)

        assert result is None

    def test_sort_path_list_empty_list(self):
        result = filesys.sort_path_list([])

        assert result == []

    def test_sort_path_list_version_numbers(self):
        paths = [
            Path("asset_v100.ma"),
            Path("asset_v2.ma"),
            Path("asset_v10.ma"),
            Path("asset_v1.ma"),
        ]

        result = filesys.sort_path_list(paths)

        assert result[0] == Path("asset_v1.ma")
        assert result[1] == Path("asset_v2.ma")
        assert result[2] == Path("asset_v10.ma")
        assert result[3] == Path("asset_v100.ma")

    def test_sort_path_list_multiple_numbers(self):
        paths = [Path("file1_v10.txt"), Path("file2_v1.txt"), Path("file1_v2.txt")]

        result = filesys.sort_path_list(paths)

        assert result[0] == Path("file1_v2.txt")
        assert result[1] == Path("file1_v10.txt")
        assert result[2] == Path("file2_v1.txt")

    def test_sort_path_list_preserves_path_type(self):
        paths = [Path("c.txt"), Path("a.txt"), Path("b.txt")]

        result = filesys.sort_path_list(paths)

        for item in result:
            assert isinstance(item, Path)

    def test_sort_path_list_with_absolute_paths(self, tmp_path):
        paths = [tmp_path / "file3.txt", tmp_path / "file1.txt", tmp_path / "file2.txt"]

        result = filesys.sort_path_list(paths)

        assert result[0] == tmp_path / "file1.txt"
        assert result[1] == tmp_path / "file2.txt"
        assert result[2] == tmp_path / "file3.txt"


class TestDeleteFilesInDirectory:
    def test_delete_files_in_directory_basic(self, tmp_path, capsys):
        # Create test files
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "file3.txt").write_text("content3")

        filesys.delete_files_in_directory(tmp_path)

        # Files should be deleted
        assert not (tmp_path / "file1.txt").exists()
        assert not (tmp_path / "file2.txt").exists()
        assert not (tmp_path / "file3.txt").exists()

        # Directory should still exist
        assert tmp_path.exists()

        captured = capsys.readouterr()
        assert "All files deleted successfully." in captured.out

    def test_delete_files_preserves_subdirectories(self, tmp_path):
        # Create files and subdirectories
        (tmp_path / "filesys.txt").write_text("content")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.txt").write_text("nested")

        filesys.delete_files_in_directory(tmp_path)

        # File in root should be deleted
        assert not (tmp_path / "filesys.txt").exists()

        # Subdirectory and its contents should remain
        assert (tmp_path / "subdir").exists()
        assert (tmp_path / "subdir" / "nested.txt").exists()

    def test_delete_files_in_empty_directory(self, tmp_path, capsys):
        filesys.delete_files_in_directory(tmp_path)

        assert tmp_path.exists()

        captured = capsys.readouterr()
        assert "All files deleted successfully." in captured.out

    def test_delete_files_with_different_extensions(self, tmp_path):
        (tmp_path / "document.txt").write_text("text")
        (tmp_path / "image.png").write_text("image")
        (tmp_path / "data.json").write_text("json")

        filesys.delete_files_in_directory(tmp_path)

        assert not (tmp_path / "document.txt").exists()
        assert not (tmp_path / "image.png").exists()
        assert not (tmp_path / "data.json").exists()

    def test_delete_files_only_affects_files(self, tmp_path):
        # Create mixed content
        (tmp_path / "filesys.txt").write_text("content")
        (tmp_path / "folder1").mkdir()
        (tmp_path / "folder2").mkdir()
        (tmp_path / "another_filesys.txt").write_text("more content")

        filesys.delete_files_in_directory(tmp_path)

        # Files deleted
        assert not (tmp_path / "filesys.txt").exists()
        assert not (tmp_path / "another_filesys.txt").exists()

        # Folders preserved
        assert (tmp_path / "folder1").exists()
        assert (tmp_path / "folder2").exists()

    def test_delete_files_with_exception_reraises(self, tmp_path, capsys):
        # Create a file
        test_file = tmp_path / "filesys.txt"
        test_file.write_text("content")

        # Make directory non-iterable by replacing it with non-Path object
        # We'll test exception handling by passing an invalid path
        invalid_path = tmp_path / "nonexistent"

        with pytest.raises(Exception):
            filesys.delete_files_in_directory(invalid_path)

        captured = capsys.readouterr()
        assert "Error occurred while deleting files." in captured.out

    def test_delete_files_handles_missing_ok(self, tmp_path):
        # Create a file
        test_file = tmp_path / "filesys.txt"
        test_file.write_text("content")

        # File exists before deletion
        assert test_file.exists()

        filesys.delete_files_in_directory(tmp_path)

        # File deleted successfully
        assert not test_file.exists()

    def test_delete_files_multiple_calls(self, tmp_path, capsys):
        # Create files
        (tmp_path / "file1.txt").write_text("content1")

        # First deletion
        filesys.delete_files_in_directory(tmp_path)

        # Create new files
        (tmp_path / "file2.txt").write_text("content2")

        # Second deletion
        filesys.delete_files_in_directory(tmp_path)

        assert not (tmp_path / "file2.txt").exists()

        captured = capsys.readouterr()
        # Should have two success messages
        assert captured.out.count("All files deleted successfully.") == 2


class TestIntegration:
    def test_create_and_delete_workflow(self, tmp_path):
        # Create structure
        structure = {"project": {"src": {}, "tests": {}}}
        filesys.create_structure(structure, tmp_path)

        # Add files to src
        src_dir = tmp_path / "project" / "src"
        (src_dir / "main.py").write_text('print("hello")')
        (src_dir / "utils.py").write_text("def helper(): pass")

        # Delete files in src
        filesys.delete_files_in_directory(src_dir)

        # Files deleted, directory remains
        assert not (src_dir / "main.py").exists()
        assert not (src_dir / "utils.py").exists()
        assert src_dir.exists()

    def test_sort_created_structure_paths(self, tmp_path):
        # Create structure with numerical names
        structure = {"folder10": {}, "folder2": {}, "folder1": {}}
        filesys.create_structure(structure, tmp_path)

        # Get paths and sort
        paths = list(tmp_path.iterdir())
        sorted_paths = filesys.sort_path_list(paths)

        assert sorted_paths[0].name == "folder1"
        assert sorted_paths[1].name == "folder2"
        assert sorted_paths[2].name == "folder10"


class TestVersionFunctions:
    """Unit tests for version file management functions."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def versioned_files(self, temp_dir):
        """Create a set of versioned test files."""
        files = [
            "shot_v001.exr",
            "shot_v002.exr",
            "shot_v005.exr",
            "render_001.png",
            "render_002.png",
            "render_010.png",
            "file_md_001.txt",
            "file_md_002.txt",
            "unversioned.exr",
            "other.png",
        ]
        for filename in files:
            (temp_dir / filename).touch()
        return temp_dir

    # Tests for filesys.get_latest_version_file_from_dir

    def test_get_latest_basic(self, versioned_files):
        """Test getting latest version with basic extension filter."""
        result = filesys.get_latest_version_file_from_dir(versioned_files, ".exr")
        assert result.name == "shot_v005.exr"

    def test_get_latest_with_substring(self, versioned_files):
        """Test getting latest version with substring filter."""
        result = filesys.get_latest_version_file_from_dir(
            versioned_files, ".txt", substring="md"
        )
        assert result.name == "file_md_002.txt"

    def test_get_latest_extension_without_dot(self, versioned_files):
        """Test extension normalization (without leading dot)."""
        result = filesys.get_latest_version_file_from_dir(versioned_files, "png")
        assert result.name == "render_010.png"

    def test_get_latest_no_matches(self, versioned_files):
        """Test returns None when no matching files found."""
        result = filesys.get_latest_version_file_from_dir(versioned_files, ".jpg")
        assert result is None

    def test_get_latest_no_versioned_files(self, temp_dir):
        """Test returns None when files exist but none are versioned."""
        (temp_dir / "unversioned.exr").touch()
        (temp_dir / "another.exr").touch()
        result = filesys.get_latest_version_file_from_dir(temp_dir, ".exr")
        assert result is None

    def test_get_latest_empty_directory(self, temp_dir):
        """Test returns None for empty directory."""
        result = filesys.get_latest_version_file_from_dir(temp_dir, ".exr")
        assert result is None

    def test_get_latest_substring_no_match(self, versioned_files):
        """Test returns None when substring doesn't match any files."""
        result = filesys.get_latest_version_file_from_dir(
            versioned_files, ".exr", substring="nonexistent"
        )
        assert result is None

    def test_get_latest_multidigit_versions(self, temp_dir):
        """Test handles multi-digit version numbers correctly."""
        for i in [1, 5, 10, 99, 100]:
            (temp_dir / f"file_{i:03d}.txt").touch()
        result = filesys.get_latest_version_file_from_dir(temp_dir, ".txt")
        assert result.name == "file_100.txt"

    def test_get_latest_ignores_directories(self, temp_dir):
        """Test ignores directories, only processes files."""
        (temp_dir / "shot_v001.exr").touch()
        (temp_dir / "shot_v999").mkdir()  # Directory with higher version
        result = filesys.get_latest_version_file_from_dir(temp_dir, ".exr")
        assert result.name == "shot_v001.exr"

    # Tests for filesys.get_next_version_from_dir

    def test_get_next_basic(self, versioned_files):
        """Test getting next version number with basic filter."""
        result = filesys.get_next_version_from_dir(versioned_files, ".exr")
        assert result == "006"

    def test_get_next_with_substring(self, versioned_files):
        """Test getting next version with substring filter."""
        result = filesys.get_next_version_from_dir(
            versioned_files, ".txt", substring="md"
        )
        assert result == "003"

    def test_get_next_extension_without_dot(self, versioned_files):
        """Test extension normalization (without leading dot)."""
        result = filesys.get_next_version_from_dir(versioned_files, "png")
        assert result == "011"

    def test_get_next_custom_padding(self, temp_dir):
        """Test custom padding length."""
        # Create files with 5-digit versions to match the padding
        (temp_dir / "shot_v00001.exr").touch()
        (temp_dir / "shot_v00002.exr").touch()
        (temp_dir / "shot_v00005.exr").touch()

        result = filesys.get_next_version_from_dir(temp_dir, ".exr", padding=5)
        assert result == "00006"

    def test_get_next_custom_padding_no_match(self, versioned_files):
        """Test custom padding returns '00001' when no files match padding length."""
        # versioned_files has 3-digit versions, asking for 5-digit padding
        result = filesys.get_next_version_from_dir(versioned_files, ".exr", padding=5)
        assert result == "00001"

    def test_get_next_custom_padding_with_match(self, temp_dir):
        """Test custom padding with matching version files."""
        (temp_dir / "shot_v00001.exr").touch()
        (temp_dir / "shot_v00005.exr").touch()

        result = filesys.get_next_version_from_dir(temp_dir, ".exr", padding=5)
        assert result == "00006"

    def test_get_next_no_matches(self, versioned_files):
        """Test returns '001' when no matching files found."""
        result = filesys.get_next_version_from_dir(versioned_files, ".jpg")
        assert result == "001"

    def test_get_next_empty_directory(self, temp_dir):
        """Test returns '001' for empty directory."""
        result = filesys.get_next_version_from_dir(temp_dir, ".exr")
        assert result == "001"

    def test_get_next_nonexistent_directory(self):
        """Test returns '001' for non-existent directory."""
        result = filesys.get_next_version_from_dir(Path("/nonexistent"), ".exr")
        assert result == "001"

    def test_get_next_none_filepath(self):
        """Test returns '001' when filepath is None."""
        result = filesys.get_next_version_from_dir(None, ".exr")
        assert result == "001"

    def test_get_next_substring_no_match(self, versioned_files):
        """Test returns '001' when substring doesn't match any files."""
        result = filesys.get_next_version_from_dir(
            versioned_files, ".exr", substring="nonexistent"
        )
        assert result == "001"

    def test_get_next_padding_2(self, temp_dir):
        """Test with 2-digit padding."""
        (temp_dir / "file_01.txt").touch()
        (temp_dir / "file_05.txt").touch()
        result = filesys.get_next_version_from_dir(temp_dir, ".txt", padding=2)
        assert result == "06"

    def test_get_next_large_version_numbers(self, temp_dir):
        """Test handles large version numbers correctly."""
        (temp_dir / "file_998.txt").touch()
        (temp_dir / "file_999.txt").touch()
        result = filesys.get_next_version_from_dir(temp_dir, ".txt")
        assert result == "1000"

    def test_get_next_ignores_non_files(self, temp_dir):
        """Test ignores directories and only processes files."""
        (temp_dir / "shot_001.exr").touch()
        (temp_dir / "shot_999").mkdir()  # Directory should be ignored
        result = filesys.get_next_version_from_dir(temp_dir, ".exr")
        assert result == "002"

    def test_get_next_requires_exact_padding(self, temp_dir):
        """Test only recognizes versions with exact padding length."""
        (temp_dir / "file_1.txt").touch()  # Only 1 digit
        (temp_dir / "file_12.txt").touch()  # Only 2 digits
        (temp_dir / "file_123.txt").touch()  # Exactly 3 digits
        result = filesys.get_next_version_from_dir(temp_dir, ".txt", padding=3)
        assert result == "124"  # Only counted file_123.txt

    # Integration tests

    def test_get_latest_then_next(self, versioned_files):
        """Test workflow: get latest, then get next version."""
        latest = filesys.get_latest_version_file_from_dir(versioned_files, ".exr")
        assert latest.name == "shot_v005.exr"

        next_ver = filesys.get_next_version_from_dir(versioned_files, ".exr")
        assert next_ver == "006"

    def test_both_functions_consistent_filtering(self, versioned_files):
        """Test both functions filter the same set of files."""
        # Both should see the same "md" files
        latest = filesys.get_latest_version_file_from_dir(
            versioned_files, ".txt", substring="md"
        )
        next_ver = filesys.get_next_version_from_dir(
            versioned_files, ".txt", substring="md"
        )

        assert latest.name == "file_md_002.txt"
        assert next_ver == "003"
