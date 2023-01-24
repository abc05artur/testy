import json
from pathlib import Path
from typing import Any, Dict

from .base_handler import DefaultMultiHandler, DefaultSingleHandler


class JsonSingleHandler(DefaultSingleHandler):

    def condition(self, variable_value: Any) -> bool:
        try:
            json.dumps(variable_value)
            return True
        except:
            return False

    def write_report(self, expected_value: Any, actual_value: Any, folder_path: Path, var_name) -> None:
        raise NotImplementedError()

    def _compare(self, expected_value: Any, actual_value: Any) -> bool:
        raise NotImplementedError()

    def _read(self, var_name: str, folder_path: Path) -> Any:
        with open(folder_path / (var_name + ".json"), "r") as f:
            var_value = json.load(f)
        return var_value

    def _write(self, var_name: str, var_value: Any, folder_path: Path) -> None:
        folder_path.mkdir(parents=True, exist_ok=True)
        with open(folder_path / (var_name + ".json"), "w") as f:
            json.dump(var_value, f, indent=2)


class JsonMultiHandler(DefaultMultiHandler):
    def condition(self, variable_value: Any) -> bool:
        try:
            s = json.dumps(variable_value)
            return len(s) <= 500
        except:
            return False

    file_name = "default_json_muti.json"

    def _read(self, folder_path: Path) -> Dict[str, Any]:
        with open(folder_path / self.file_name, "r") as f:
            ans_d = json.load(f)
        return ans_d

    def _write(self, var_dict: Dict[str, Any], folder_path: Path) -> None:
        folder_path.mkdir(parents=True, exist_ok=True)
        with open(folder_path / self.file_name, "w") as f:
            json.dump(var_dict, f, indent=2)

    def _compare(self, expected_value: Any, actual_value: Any) -> bool:
        return json.dumps(expected_value) == json.dumps(actual_value)
