import csv
import json
from xml.etree import ElementTree
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Union

import yaml


# -----Json--------------------------------------------------------------------


JSON_TYPE = Union[dict, list, int, float, bool, str, None]
JSON_EXPORT_TYPE = Union[dict[JSON_TYPE, JSON_TYPE], list[JSON_TYPE]]


def export_data_to_json(
    path: Path, data: JSON_EXPORT_TYPE, overwrite: bool = False
) -> None:
    """
    Export dict to JSON file path.

    Args:
        path (Path): the file path to place the .json file.
        data (JSON_EXPORT_TYPE): the data to export into the .json file.
        overwrite(bool): to overwrite JSON file if it already exists in path.
            Defaults to False.
    """
    if not overwrite and path.exists():
        return

    with open(path, "w") as outfile:
        json.dump(data, outfile, indent=4)


def import_data_from_json(filepath: Path) -> Optional[dict]:
    """
    Import data from a .json file.

    Args:
        filepath (Path): the filepath to the JSON file to extract data from.
    Returns:
        any: will return data if JSON file exists, None if it doesn't.
    """
    if not filepath.exists():
        return None

    with open(filepath) as file:
        data = json.load(file)
        return data


# -----Yaml--------------------------------------------------------------------


YAML_TYPE = Union[dict, list, int, float, bool, str, None]
YAML_EXPORT_TYPE = Union[dict[YAML_TYPE, YAML_TYPE], list[YAML_TYPE]]


def export_data_to_yaml(
    path: Path, data: YAML_EXPORT_TYPE, overwrite: bool = False
) -> None:
    """
    Export dict to YAML file path.

    Args:
        path (Path): the file path to place the .yaml file.
        data (YAML_EXPORT_TYPE): the data to export into the .yaml file.
        overwrite(bool): to overwrite YAML file if it already exists in path.
            Defaults to False.
    """
    if not overwrite and path.exists():
        return

    with open(path, "w") as outfile:
        yaml.dump(data, outfile, default_flow_style=False, sort_keys=False)


def import_data_from_yaml(filepath: Path) -> Optional[dict]:
    """
    Import data from a .yaml file.

    Args:
        filepath (Path): the filepath to the YAML file to extract data from.
    Returns:
        any: will return data if YAML file exists, None if it doesn't.
    """
    if not filepath.exists():
        return None

    with open(filepath) as file:
        data = yaml.safe_load(file)
        return data


# -----XML---------------------------------------------------------------------


XML_PARSED_TYPE = Union[dict, list, str]


def export_data_to_xml(
    path: Path, data: Union[dict, list], overwrite: bool = False, root_tag: str = "root"
) -> None:
    """
    Export dict to XML file path.

    Args:
        path (Path): the file path to place the .xml file.
        data (dict|list): the data to export into the .xml file.
        overwrite(bool): to overwrite XML file if it already exists in path.
            Defaults to False.
        root_tag (str): the tag name for the root element. Defaults to "root".
    """
    if not overwrite and path.exists():
        return

    root = _dict_to_xml(data, root_tag)
    tree = ElementTree.ElementTree(root)
    ElementTree.indent(tree, space="    ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def _dict_to_xml(data: XML_PARSED_TYPE, tag: str) -> ElementTree.Element:
    """Convert dict/list to XML Element."""
    element = ElementTree.Element(tag)

    if isinstance(data, dict):
        for key, val in data.items():
            child = _dict_to_xml(val, key)
            element.append(child)
    elif isinstance(data, list):
        for item in data:
            child = _dict_to_xml(item, "item")
            element.append(child)
    else:
        element.text = str(data)

    return element


def import_data_from_xml(filepath: Path) -> Optional[dict]:
    """
    Import data from a .xml file.

    Args:
        filepath (Path): the filepath to the XML file to extract data from.
    Returns:
        any: will return data if XML file exists, None if it doesn't.
    """
    if not filepath.exists():
        return None

    tree = ElementTree.parse(filepath)
    root = tree.getroot()
    data = _xml_to_dict(root)
    return data


def _xml_to_dict(element: ElementTree.Element) -> Union[dict, list, str]:
    """Convert XML Element to dict."""
    # If element has no children, return its text
    if len(element) == 0:
        return element.text if element.text else ""

    # Check if all children have the same tag (list-like)
    children_tags = [child.tag for child in element]
    if len(set(children_tags)) == 1:
        return [_xml_to_dict(child) for child in element]

    # Otherwise, treat as dict
    result = {}
    for child in element:
        child_data = _xml_to_dict(child)
        if child.tag in result:
            # Handle duplicate keys by converting to list
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_data)
        else:
            result[child.tag] = child_data

    return result


# -----CSV---------------------------------------------------------------------


CSV_EXPORT_TYPE = Union[list[dict[str, Any]], list[list[Any]]]

CSV_IMPORT_DICT_TYPE = list[dict[str, str]]  # as_dict=True
CSV_IMPORT_LIST_TYPE = list[list[str]]  # as_dict=False
CSV_IMPORT_TYPE = Union[CSV_IMPORT_DICT_TYPE, CSV_IMPORT_LIST_TYPE]


def export_data_to_csv(
    path: Path,
    data: CSV_EXPORT_TYPE,
    overwrite: bool = False,
    fieldnames: Optional[list[str]] = None,
) -> None:
    """
    Export list of dicts or list of lists to CSV file path.

    Args:
        path (Path): the file path to place the .csv file.
        data (CSV_EXPORT_TYPE): the data to export into the .csv file.
            For list of dicts, keys become column headers.
            For list of lists, first row is treated as headers unless fieldnames
                provided.
        overwrite(bool): to overwrite CSV file if it already exists in path.
            Defaults to False.
        fieldnames (list[str]): optional column headers for list of lists.
            If not provided and data is list of dicts, uses dict keys.
            If not provided and data is list of lists, uses first row as headers.
    """
    if not overwrite and path.exists():
        return

    if not data:
        return

    with open(path, "w", newline="") as outfile:
        if isinstance(data[0], dict):
            # List of dicts
            if fieldnames is None:
                fieldnames = list(data[0].keys())
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        else:
            # List of lists
            writer = csv.writer(outfile)
            if fieldnames:
                writer.writerow(fieldnames)
            writer.writerows(data)


def import_data_from_csv(
    filepath: Path, as_dict: bool = True
) -> Optional[CSV_IMPORT_TYPE]:
    """
    Import data from a .csv file.

    Args:
        filepath (Path): the filepath to the CSV file to extract data from.
        as_dict (bool): if True, returns list of dicts with headers as keys.
            If False, returns list of lists including header row.
            Defaults to True.
    Returns:
        Optional[CSV_IMPORT_TYPE]: will return data if CSV file exists, None
            if it doesn't.
    """
    if not filepath.exists():
        return None

    with open(filepath, newline="") as file:
        if as_dict:
            reader = csv.DictReader(file)
            data = list(reader)
        else:
            reader = csv.reader(file)
            data = list(reader)
        return data
