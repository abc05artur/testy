import json
from typing import Any


def is_json(var_value: Any) -> bool:
    try:
        json.dumps(var_value)
        return True
    except:
        return False


def is_json_short(var_value: Any) -> bool:
    try:
        s = json.dumps(var_value)
        return len(s) <= 500
    except:
        return False


def condition_for_dataframe_handler() -> bool:
    try:
        import pandas
        return True
    finally:
        return False
