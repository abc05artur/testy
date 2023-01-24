import json
from pathlib import Path
from typing import Any

from .base_handler import DefaultSingleHandler


class ExceptionHandler(DefaultSingleHandler):

    def condition(self, variable_value: Any) -> bool:
        return isinstance(variable_value, BaseException)

    def exception_to_dict(self, e: BaseException):
        ans = dict()
        ans["type"] = str(type(e))
        ans["args"] = e.args
        if e.__cause__ is not None:
            ans["inner"] = self.exception_to_dict(e.__cause__)
        return ans

    def write_report(self, expected_value: Any, actual_value: Any, folder_path: Path, var_name) -> None:
        if isinstance(expected_value, Exception):
            expected_value = self.exception_to_dict(expected_value)
        expected_value = json.dumps(expected_value, indent=2)
        if isinstance(actual_value, Exception):
            actual_value = self.exception_to_dict(actual_value)
        actual_value = json.dumps(actual_value, indent=2)
        folder_path.mkdir(parents=True, exist_ok=True)
        with open(folder_path / (var_name + ".json"), "w") as f:
            f.write(expected_value)
            f.write(actual_value)

    def _compare(self, expected_value: Any, actual_value: Any) -> bool:
        if isinstance(expected_value, Exception):
            expected_value = self.exception_to_dict(expected_value)
        expected_value = json.dumps(expected_value, indent=2)
        if isinstance(actual_value, Exception):
            actual_value = self.exception_to_dict(actual_value)
        actual_value = json.dumps(actual_value, indent=2)
        return actual_value == expected_value

    def _read(self, var_name: str, folder_path: Path) -> Any:
        with open(folder_path / (var_name + ".json"), "r") as f:
            var_value = json.load(f)
        return var_value

    def _write(self, var_name: str, var_value: Any, folder_path: Path) -> None:
        if isinstance(var_value, Exception):
            var_value = self.exception_to_dict(var_value)
        folder_path.mkdir(parents=True, exist_ok=True)
        with open(folder_path / (var_name + ".json"), "w") as f:
            json.dump(var_value, f, indent=2)
