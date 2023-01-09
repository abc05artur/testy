import json
from typing import Any


class TestyError(Exception):
    "raised when an error occurs in testy"
    pass


def is_json(var_value: Any) -> bool:
    try:
        json.dumps(var_value)
        return True
    except:
        return False
