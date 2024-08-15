import os
import json
from typing import Dict, Any


def json_load(file_path: str, default=None) -> Dict[str, Any]:
    """
    Load JSON data from a file.

    Args:
        file_path (str): Path to the JSON file.
        default (Dict[str, Any], optional): Default value if file doesn't exist. Defaults to None.

    Returns:
        Dict[str, Any]: Loaded JSON data or default value.

    Raises:
        ValueError: If the file extension is not .json.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    if not file_path.lower().endswith('.json'):
        raise ValueError("File extension must be .json")

    if default is None:
        default = {}
    data = default

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data.update(json.load(f))
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(f"Invalid JSON in {file_path}: {str(e)}", e.doc, e.pos)

    return data


def json_dump(file_path: str, data: Dict[str, Any], indent: int = 4):
    """
    Write JSON data to a file.

    Args:
        file_path (str): Path to the JSON file.
        data (Dict[str, Any]): Data to be written.
        indent (int, optional): Number of spaces for indentation. Defaults to 4.

    Raises:
        ValueError: If the file extension is not .json.
        OSError: If there's an error writing to the file.
    """
    if not file_path.lower().endswith('.json'):
        raise ValueError("File extension must be .json")

    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except OSError as e:
        raise OSError(f"Error writing to {file_path}: {str(e)}")


def json_update(file_path: str, new_data: Dict[str, Any], indent: int = 4):
    """
    Update existing JSON file with new data.

    Args:
        file_path (str): Path to the JSON file.
        new_data (Dict[str, Any]): New data to be added or updated.
        indent (int, optional): Number of spaces for indentation. Defaults to 4.

    Raises:
        ValueError: If the file extension is not .json.
        json.JSONDecodeError: If the existing file contains invalid JSON.
        OSError: If there's an error reading from or writing to the file.
    """
    if not file_path.lower().endswith('.json'):
        raise ValueError("File extension must be .json")

    try:
        data = json_load(file_path, default={})
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in existing file {file_path}: {str(e)}", e.doc, e.pos)

    data.update(new_data)

    try:
        json_dump(file_path, data, indent)
    except OSError as e:
        raise OSError(f"Error updating {file_path}: {str(e)}")


if __name__ == '__main__':
    config = json_load('config.json', default={
        'device': 'PC',
        'model_name': '-',
        '2':'1'
    })
    json_update('config.json', config)
    print(config)
