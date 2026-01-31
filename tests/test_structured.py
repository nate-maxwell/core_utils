import csv
import json
from xml.etree import ElementTree

import pytest
import yaml

from core_utils import structured


# -----JSON Tests--------------------------------------------------------------


class TestJSON:
    @pytest.fixture
    def json_data(self):
        return {
            "name": "Bob",
            "age": 78,
            "active": True,
            "balance": 123.45,
            "tags": ["python", "testing"],
            "metadata": None,
        }

    @pytest.fixture
    def json_file(self, tmp_path):
        return tmp_path / "test.json"

    def test_export_data_to_json_creates_file(self, json_file, json_data):
        structured.export_data_to_json(json_file, json_data)
        assert json_file.exists()

    def test_export_data_to_json_writes_correct_data(self, json_file, json_data):
        structured.export_data_to_json(json_file, json_data)
        with open(json_file) as f:
            loaded_data = json.load(f)
        assert loaded_data == json_data

    def test_export_data_to_json_does_not_overwrite_by_default(
        self, json_file, json_data
    ):
        original_data = {"original": "data"}
        structured.export_data_to_json(json_file, original_data)
        structured.export_data_to_json(json_file, json_data, overwrite=False)

        loaded_data = structured.import_data_from_json(json_file)
        assert loaded_data == original_data

    def test_export_data_to_json_overwrites_when_specified(self, json_file, json_data):
        original_data = {"original": "data"}
        structured.export_data_to_json(json_file, original_data)
        structured.export_data_to_json(json_file, json_data, overwrite=True)

        loaded_data = structured.import_data_from_json(json_file)
        assert loaded_data == json_data

    def test_import_data_from_json_returns_correct_data(self, json_file, json_data):
        structured.export_data_to_json(json_file, json_data)
        loaded_data = structured.import_data_from_json(json_file)
        assert loaded_data == json_data

    def test_import_data_from_json_returns_none_for_nonexistent_file(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.json"
        assert structured.import_data_from_json(nonexistent_file) is None

    def test_json_roundtrip_with_list(self, json_file):
        data = [1, 2, 3, "test", True, None]
        structured.export_data_to_json(json_file, data)
        loaded_data = structured.import_data_from_json(json_file)
        assert loaded_data == data


# -----YAML Tests--------------------------------------------------------------


class TestYAML:
    @pytest.fixture
    def yaml_data(self):
        return {
            "name": "Bob",
            "age": 78,
            "active": False,
            "balance": 678.90,
            "tags": ["yaml", "config"],
            "metadata": None,
        }

    @pytest.fixture
    def yaml_file(self, tmp_path):
        return tmp_path / "test.yaml"

    def test_export_data_to_yaml_creates_file(self, yaml_file, yaml_data):
        structured.export_data_to_yaml(yaml_file, yaml_data)
        assert yaml_file.exists()

    def test_export_data_to_yaml_writes_correct_data(self, yaml_file, yaml_data):
        structured.export_data_to_yaml(yaml_file, yaml_data)
        with open(yaml_file) as f:
            loaded_data = yaml.safe_load(f)
        assert loaded_data == yaml_data

    def test_export_data_to_yaml_does_not_overwrite_by_default(
        self, yaml_file, yaml_data
    ):
        original_data = {"original": "data"}
        structured.export_data_to_yaml(yaml_file, original_data)
        structured.export_data_to_yaml(yaml_file, yaml_data, overwrite=False)

        loaded_data = structured.import_data_from_yaml(yaml_file)
        assert loaded_data == original_data

    def test_export_data_to_yaml_overwrites_when_specified(self, yaml_file, yaml_data):
        original_data = {"original": "data"}
        structured.export_data_to_yaml(yaml_file, original_data)
        structured.export_data_to_yaml(yaml_file, yaml_data, overwrite=True)

        loaded_data = structured.import_data_from_yaml(yaml_file)
        assert loaded_data == yaml_data

    def test_import_data_from_yaml_returns_correct_data(self, yaml_file, yaml_data):
        structured.export_data_to_yaml(yaml_file, yaml_data)
        loaded_data = structured.import_data_from_yaml(yaml_file)
        assert loaded_data == yaml_data

    def test_import_data_from_yaml_returns_none_for_nonexistent_file(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.yaml"
        assert structured.import_data_from_yaml(nonexistent_file) is None

    def test_yaml_roundtrip_with_list(self, yaml_file):
        data = [1, 2, 3, "test", True, None]
        structured.export_data_to_yaml(yaml_file, data)
        loaded_data = structured.import_data_from_yaml(yaml_file)
        assert loaded_data == data


# -----XML Tests---------------------------------------------------------------


class TestXML:
    @pytest.fixture
    def xml_data(self):
        return {
            "name": "Bob",
            "age": "78",
            "city": "Lincoln",
        }

    @pytest.fixture
    def xml_file(self, tmp_path):
        return tmp_path / "test.xml"

    def test_export_data_to_xml_creates_file(self, xml_file, xml_data):
        structured.export_data_to_xml(xml_file, xml_data)
        assert xml_file.exists()

    def test_export_data_to_xml_creates_valid_xml(self, xml_file, xml_data):
        structured.export_data_to_xml(xml_file, xml_data)
        tree = ElementTree.parse(xml_file)
        assert tree.getroot() is not None

    def test_export_data_to_xml_does_not_overwrite_by_default(self, xml_file):
        original_data = {"name": "Alice", "age": "30"}
        structured.export_data_to_xml(xml_file, original_data)

        new_data = {"name": "Bob", "age": "25"}
        structured.export_data_to_xml(xml_file, new_data, overwrite=False)

        loaded_data = structured.import_data_from_xml(xml_file)
        assert loaded_data == original_data

    def test_export_data_to_xml_overwrites_when_specified(self, xml_file):
        original_data = {"name": "Alice", "age": "30"}
        structured.export_data_to_xml(xml_file, original_data)

        new_data = {"name": "Bob", "age": "25"}
        structured.export_data_to_xml(xml_file, new_data, overwrite=True)

        loaded_data = structured.import_data_from_xml(xml_file)
        assert loaded_data == new_data

    def test_export_data_to_xml_custom_root_tag(self, xml_file, xml_data):
        structured.export_data_to_xml(xml_file, xml_data, root_tag="custom")
        tree = ElementTree.parse(xml_file)
        assert tree.getroot().tag == "custom"

    def test_import_data_from_xml_returns_correct_data(self, xml_file, xml_data):
        structured.export_data_to_xml(xml_file, xml_data)
        loaded_data = structured.import_data_from_xml(xml_file)
        assert loaded_data == xml_data

    def test_import_data_from_xml_returns_none_for_nonexistent_file(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.xml"
        assert structured.import_data_from_xml(nonexistent_file) is None

    def test_xml_roundtrip_with_list(self, xml_file):
        data = ["item1", "item2", "item3"]
        structured.export_data_to_xml(xml_file, data)
        loaded_data = structured.import_data_from_xml(xml_file)
        assert loaded_data == data

    def test_xml_roundtrip_with_flat_dict(self, xml_file):
        data = {
            "name": "Alice",
            "age": "30",
            "city": "NYC",
        }
        structured.export_data_to_xml(xml_file, data)
        loaded_data = structured.import_data_from_xml(xml_file)
        assert loaded_data == data

    def test_xml_roundtrip_with_nested_dict(self, xml_file):
        # Use a structure that round-trips correctly
        data = {
            "user": "Bob",
            "settings": {
                "theme": "dark",
                "notifications": "enabled",
            },
        }
        structured.export_data_to_xml(xml_file, data)
        loaded_data = structured.import_data_from_xml(xml_file)
        assert loaded_data == data

    def test_xml_handles_mixed_content(self, xml_file):
        data = {
            "title": "Test",
            "items": ["a", "b", "c"],
            "count": "3",
        }
        structured.export_data_to_xml(xml_file, data)
        loaded_data = structured.import_data_from_xml(xml_file)
        assert loaded_data == data


# -----CSV Tests---------------------------------------------------------------


class TestCSV:
    @pytest.fixture
    def csv_dict_data(self):
        return [
            {"name": "Alice", "age": "30", "city": "NYC"},
            {"name": "Bob", "age": "78", "city": "Lincoln"},
            {"name": "Charlie", "age": "35", "city": "Chicago"},
        ]

    @pytest.fixture
    def csv_list_data(self):
        return [
            ["name", "age", "city"],
            ["Alice", "30", "NYC"],
            ["Bob", "78", "Lincoln"],
            ["Charlie", "35", "Chicago"],
        ]

    @pytest.fixture
    def csv_file(self, tmp_path):
        return tmp_path / "test.csv"

    def test_export_data_to_csv_creates_file_from_dicts(self, csv_file, csv_dict_data):
        structured.export_data_to_csv(csv_file, csv_dict_data)
        assert csv_file.exists()

    def test_export_data_to_csv_writes_correct_data_from_dicts(
        self, csv_file, csv_dict_data
    ):
        structured.export_data_to_csv(csv_file, csv_dict_data)
        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            loaded_data = list(reader)
        assert loaded_data == csv_dict_data

    def test_export_data_to_csv_creates_file_from_lists(self, csv_file, csv_list_data):
        structured.export_data_to_csv(csv_file, csv_list_data)
        assert csv_file.exists()

    def test_export_data_to_csv_writes_correct_data_from_lists(
        self, csv_file, csv_list_data
    ):
        structured.export_data_to_csv(csv_file, csv_list_data)
        with open(csv_file, newline="") as f:
            reader = csv.reader(f)
            loaded_data = list(reader)
        assert loaded_data == csv_list_data

    def test_export_data_to_csv_with_custom_fieldnames(self, csv_file):
        data = [["Alice", "30"], ["Bob", "25"]]
        fieldnames = ["name", "age"]
        structured.export_data_to_csv(csv_file, data, fieldnames=fieldnames)

        with open(csv_file, newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
        assert rows[0] == fieldnames
        assert rows[1:] == data

    def test_export_data_to_csv_does_not_overwrite_by_default(
        self, csv_file, csv_dict_data
    ):
        original_data = [{"original": "data"}]
        structured.export_data_to_csv(csv_file, original_data)
        structured.export_data_to_csv(csv_file, csv_dict_data, overwrite=False)

        loaded_data = structured.import_data_from_csv(csv_file, as_dict=True)
        assert loaded_data == original_data

    def test_export_data_to_csv_overwrites_when_specified(
        self, csv_file, csv_dict_data
    ):
        original_data = [{"original": "data"}]
        structured.export_data_to_csv(csv_file, original_data)
        structured.export_data_to_csv(csv_file, csv_dict_data, overwrite=True)

        loaded_data = structured.import_data_from_csv(csv_file, as_dict=True)
        assert loaded_data == csv_dict_data

    def test_export_data_to_csv_handles_empty_data(self, csv_file):
        structured.export_data_to_csv(csv_file, [])
        assert not csv_file.exists()

    def test_import_data_from_csv_as_dict(self, csv_file, csv_dict_data):
        structured.export_data_to_csv(csv_file, csv_dict_data)
        loaded_data = structured.import_data_from_csv(csv_file, as_dict=True)
        assert loaded_data == csv_dict_data

    def test_import_data_from_csv_as_list(self, csv_file, csv_list_data):
        structured.export_data_to_csv(csv_file, csv_list_data)
        loaded_data = structured.import_data_from_csv(csv_file, as_dict=False)
        assert loaded_data == csv_list_data

    def test_import_data_from_csv_returns_none_for_nonexistent_file(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.csv"
        assert structured.import_data_from_csv(nonexistent_file) is None

    def test_csv_roundtrip_dict(self, csv_file, csv_dict_data):
        structured.export_data_to_csv(csv_file, csv_dict_data)
        loaded_data = structured.import_data_from_csv(csv_file, as_dict=True)
        assert loaded_data == csv_dict_data

    def test_csv_roundtrip_list(self, csv_file, csv_list_data):
        structured.export_data_to_csv(csv_file, csv_list_data)
        loaded_data = structured.import_data_from_csv(csv_file, as_dict=False)
        assert loaded_data == csv_list_data
