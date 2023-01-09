import json
from pathlib import Path
from typing import Any

from .base_handler import SingleHandler


class JsonSingleHandler(SingleHandler):

    def write_report(self, expected_answer: Any, actual_answer: Any, folder_path: Path) -> None:
        raise NotImplementedError()

    def is_same(self, expected_answer: Any, actual_answer: Any) -> bool:
        raise NotImplementedError()

    def user_def_read(self, var_name: str, folder_path: Path) -> Any:
        raise NotImplementedError()

    def user_def_write(self, var_name: str, var_value: Any, folder_path: Path) -> None:
        with open(folder_path / (var_name + ".json")) as f:
            json.dump(var_value, f, indent=4)