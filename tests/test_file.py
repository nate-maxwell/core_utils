from pathlib import Path

import pytest

from core import file


# -----create_structure Tests--------------------------------------------------


class TestCreateStructure:
    def test_create_structure_simple(self, tmp_path, capsys):
        structure = {"folder1": {}, "folder2": {}}

        file.create_structure(structure, tmp_path)

        assert (tmp_path / "folder1").exists()
        assert (tmp_path / "folder1").is_dir()
        assert (tmp_path / "folder2").exists()
        assert (tmp_path / "folder2").is_dir()

        captured = capsys.readouterr()
        assert "written to" in captured.out

    def test_create_structure_nested(self, tmp_path):
        structure = {"assets": {"model": {}, "texture": {}, "anim": {}}, "config": {}}

        file.create_structure(structure, tmp_path)

        assert (tmp_path / "assets").exists()
        assert (tmp_path / "assets" / "model").exists()
        assert (tmp_path / "assets" / "texture").exists()
        assert (tmp_path / "assets" / "anim").exists()
        assert (tmp_path / "config").exists()

    def test_create_structure_deeply_nested(self, tmp_path):
        structure = {"level1": {"level2": {"level3": {"level4": {}}}}}

        file.create_structure(structure, tmp_path)

        assert (tmp_path / "level1" / "level2" / "level3" / "level4").exists()

    def test_create_structure_empty_dict(self, tmp_path):
        structure = {}

        file.create_structure(structure, tmp_path)

        # tmp_path should still exist
        assert tmp_path.exists()

    def test_create_structure_single_folder(self, tmp_path):
        structure = {"single": {}}

        file.create_structure(structure, tmp_path)

        assert (tmp_path / "single").exists()

    def test_create_structure_multiple_levels(self, tmp_path):
        structure = {
            "src": {"main": {}, "test": {}},
            "docs": {},
            "build": {"output": {}},
        }

        file.create_structure(structure, tmp_path)

        assert (tmp_path / "src" / "main").exists()
        assert (tmp_path / "src" / "test").exists()
        assert (tmp_path / "docs").exists()
        assert (tmp_path / "build" / "output").exists()

    def test_create_structure_prints_confirmation(self, tmp_path, capsys):
        structure = {"test": {}}

        file.create_structure(structure, tmp_path)

        captured = capsys.readouterr()
        assert str(structure) in captured.out
        assert str(tmp_path) in captured.out

    def test_create_structure_in_nonexistent_destination(self, tmp_path):
        destination = tmp_path / "new" / "nested" / "path"
        structure = {"folder": {}}

        file.create_structure(structure, destination)

        assert destination.exists()
        assert (destination / "folder").exists()


# -----sort_path_list Tests----------------------------------------------------


class TestSortPathList:
    def test_sort_path_list_alphabetical(self):
        paths = [Path("zebra.txt"), Path("alpha.txt"), Path("beta.txt")]

        result = file.sort_path_list(paths)

        assert result[0] == Path("alpha.txt")
        assert result[1] == Path("beta.txt")
        assert result[2] == Path("zebra.txt")

    def test_sort_path_list_numerical(self):
        paths = [Path("file10.txt"), Path("file2.txt"), Path("file1.txt")]

        result = file.sort_path_list(paths)

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

        result = file.sort_path_list(paths)

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

        result = file.sort_path_list(paths)

        assert result[0] == Path("folder/file1.txt")
        assert result[1] == Path("folder/file2.txt")
        assert result[2] == Path("folder/file10.txt")

    def test_sort_path_list_single_item(self):
        paths = [Path("single.txt")]

        result = file.sort_path_list(paths)

        assert result == paths

    def test_sort_path_list_none_input(self):
        result = file.sort_path_list(None)

        assert result is None

    def test_sort_path_list_empty_list(self):
        result = file.sort_path_list([])

        assert result == []

    def test_sort_path_list_version_numbers(self):
        paths = [
            Path("asset_v100.ma"),
            Path("asset_v2.ma"),
            Path("asset_v10.ma"),
            Path("asset_v1.ma"),
        ]

        result = file.sort_path_list(paths)

        assert result[0] == Path("asset_v1.ma")
        assert result[1] == Path("asset_v2.ma")
        assert result[2] == Path("asset_v10.ma")
        assert result[3] == Path("asset_v100.ma")

    def test_sort_path_list_multiple_numbers(self):
        paths = [Path("file1_v10.txt"), Path("file2_v1.txt"), Path("file1_v2.txt")]

        result = file.sort_path_list(paths)

        assert result[0] == Path("file1_v2.txt")
        assert result[1] == Path("file1_v10.txt")
        assert result[2] == Path("file2_v1.txt")

    def test_sort_path_list_preserves_path_type(self):
        paths = [Path("c.txt"), Path("a.txt"), Path("b.txt")]

        result = file.sort_path_list(paths)

        for item in result:
            assert isinstance(item, Path)

    def test_sort_path_list_with_absolute_paths(self, tmp_path):
        paths = [tmp_path / "file3.txt", tmp_path / "file1.txt", tmp_path / "file2.txt"]

        result = file.sort_path_list(paths)

        assert result[0] == tmp_path / "file1.txt"
        assert result[1] == tmp_path / "file2.txt"
        assert result[2] == tmp_path / "file3.txt"


# -----delete_files_in_directory Tests-----------------------------------------


class TestDeleteFilesInDirectory:
    def test_delete_files_in_directory_basic(self, tmp_path, capsys):
        # Create test files
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "file3.txt").write_text("content3")

        file.delete_files_in_directory(tmp_path)

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
        (tmp_path / "file.txt").write_text("content")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.txt").write_text("nested")

        file.delete_files_in_directory(tmp_path)

        # File in root should be deleted
        assert not (tmp_path / "file.txt").exists()

        # Subdirectory and its contents should remain
        assert (tmp_path / "subdir").exists()
        assert (tmp_path / "subdir" / "nested.txt").exists()

    def test_delete_files_in_empty_directory(self, tmp_path, capsys):
        file.delete_files_in_directory(tmp_path)

        assert tmp_path.exists()

        captured = capsys.readouterr()
        assert "All files deleted successfully." in captured.out

    def test_delete_files_with_different_extensions(self, tmp_path):
        (tmp_path / "document.txt").write_text("text")
        (tmp_path / "image.png").write_text("image")
        (tmp_path / "data.json").write_text("json")

        file.delete_files_in_directory(tmp_path)

        assert not (tmp_path / "document.txt").exists()
        assert not (tmp_path / "image.png").exists()
        assert not (tmp_path / "data.json").exists()

    def test_delete_files_only_affects_files(self, tmp_path):
        # Create mixed content
        (tmp_path / "file.txt").write_text("content")
        (tmp_path / "folder1").mkdir()
        (tmp_path / "folder2").mkdir()
        (tmp_path / "another_file.txt").write_text("more content")

        file.delete_files_in_directory(tmp_path)

        # Files deleted
        assert not (tmp_path / "file.txt").exists()
        assert not (tmp_path / "another_file.txt").exists()

        # Folders preserved
        assert (tmp_path / "folder1").exists()
        assert (tmp_path / "folder2").exists()

    def test_delete_files_with_exception_reraises(self, tmp_path, capsys):
        # Create a file
        test_file = tmp_path / "file.txt"
        test_file.write_text("content")

        # Make directory non-iterable by replacing it with non-Path object
        # We'll test exception handling by passing an invalid path
        invalid_path = tmp_path / "nonexistent"

        with pytest.raises(Exception):
            file.delete_files_in_directory(invalid_path)

        captured = capsys.readouterr()
        assert "Error occurred while deleting files." in captured.out

    def test_delete_files_handles_missing_ok(self, tmp_path):
        # Create a file
        test_file = tmp_path / "file.txt"
        test_file.write_text("content")

        # File exists before deletion
        assert test_file.exists()

        file.delete_files_in_directory(tmp_path)

        # File deleted successfully
        assert not test_file.exists()

    def test_delete_files_multiple_calls(self, tmp_path, capsys):
        # Create files
        (tmp_path / "file1.txt").write_text("content1")

        # First deletion
        file.delete_files_in_directory(tmp_path)

        # Create new files
        (tmp_path / "file2.txt").write_text("content2")

        # Second deletion
        file.delete_files_in_directory(tmp_path)

        assert not (tmp_path / "file2.txt").exists()

        captured = capsys.readouterr()
        # Should have two success messages
        assert captured.out.count("All files deleted successfully.") == 2


# -----Integration Tests-------------------------------------------------------


class TestIntegration:
    def test_create_and_delete_workflow(self, tmp_path):
        # Create structure
        structure = {"project": {"src": {}, "tests": {}}}
        file.create_structure(structure, tmp_path)

        # Add files to src
        src_dir = tmp_path / "project" / "src"
        (src_dir / "main.py").write_text('print("hello")')
        (src_dir / "utils.py").write_text("def helper(): pass")

        # Delete files in src
        file.delete_files_in_directory(src_dir)

        # Files deleted, directory remains
        assert not (src_dir / "main.py").exists()
        assert not (src_dir / "utils.py").exists()
        assert src_dir.exists()

    def test_sort_created_structure_paths(self, tmp_path):
        # Create structure with numerical names
        structure = {"folder10": {}, "folder2": {}, "folder1": {}}
        file.create_structure(structure, tmp_path)

        # Get paths and sort
        paths = list(tmp_path.iterdir())
        sorted_paths = file.sort_path_list(paths)

        assert sorted_paths[0].name == "folder1"
        assert sorted_paths[1].name == "folder2"
        assert sorted_paths[2].name == "folder10"
