import json
from typing import Any


def update_json_in_string(string: str, key: str, value: Any) -> str:
    string_in_json = json.loads(string)
    string_in_json[key] = value

    return json.dumps(string_in_json)
