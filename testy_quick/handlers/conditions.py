import json
from typing import Any


def is_json(var_value: Any) -> bool:
    try:
        json.dumps(var_value)
        return True
    except:
        return False
