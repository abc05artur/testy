from pathlib import Path
from typing import Any, Dict

import pandas as pd

from tests.tools import delete_f, temp_data_path
from testy_quick.low_level import TestyError
from testy_quick.variable_handlers import SingleHandler, MultiHandler


class PoorelyImplemented(SingleHandler):

    def write_report(self, expected_value: Any, actual_value: Any, folder_path: Path, var_name: str) -> None:
        pass

    def _compare(self, expected_value: Any, actual_value: Any) -> bool:
        return True

    def _read(self, var_name: str, folder_path: Path) -> Any:
        with open(folder_path / (var_name + ".txt"), 'r') as f:
            var_value = f.read()
        return var_value

    def _write(self, var_name: str, var_value: Any, folder_path: Path) -> None:
        with open(folder_path / (var_name + ".txt"), 'w') as f:
            f.write(var_value)


class Proper_impl(SingleHandler):

    def _compare(self, expected_value: Any, actual_value: Any) -> bool:
        return True

    def _read(self, var_name: str, folder_path: Path) -> Any:
        with open(folder_path / (var_name + ".txt"), 'r') as f:
            var_value = f.read()
        return var_value

    def _write(self, var_name: str, var_value: Any, folder_path: Path) -> None:
        folder_path.mkdir(parents=True, exist_ok=True)
        with open(folder_path / (var_name + ".txt"), 'w') as f:
            f.write(var_value)

    def get_report(self, expected_value: Any, actual_value: Any, var_name: str) -> str:
        return "here is your report"


class MultiImp(MultiHandler):

    def _read(self, folder_path: Path) -> Dict[str, Any]:
        s = pd.read_csv(folder_path / "MultiImp.csv").set_index("index")["values"]
        answer = s.to_dict()
        return answer

    def _write(self, var_dict: Dict[str, Any], folder_path: Path) -> None:
        folder_path.mkdir(parents=True, exist_ok=True)
        s = pd.Series(var_dict)
        s.name = "values"
        s.index.name = "index"
        df: pd.DataFrame = s.reset_index()
        df.to_csv(folder_path / "MultiImp.csv", index=False)

    def _compare(self, expected_value: Any, actual_value: Any) -> bool:
        pass


poor = PoorelyImplemented()
h2 = Proper_impl()
h3 = MultiImp()


def test_single_empty():
    delete_f(temp_data_path)
    data = {}
    poor.write(data, temp_data_path)
    delete_f(temp_data_path)


def test_single_poor():
    delete_f(temp_data_path)
    data = {"1": "1",
            "2": 2}
    exc = None
    try:
        poor.write(data, temp_data_path)
    except Exception as e:
        exc = e
    assert isinstance(exc, TestyError)
    assert isinstance(exc.__cause__, FileNotFoundError)
    delete_f(temp_data_path)


def test_multi():
    delete_f(temp_data_path)
    d = {
        "x1": 2,
        "x2": 3,
    }
    h3.write(d, temp_data_path)
    d2 = h3.read(d.keys(), temp_data_path)
    assert len(d2) == len(d)
    for k in d:
        assert d[k] == d2[k]
    delete_f(temp_data_path)


def test_single():
    delete_f(temp_data_path)
    data = {"1": "1",
            "2": "2"}
    h2.write(data, temp_data_path)
    assert (temp_data_path / "1.txt").is_file()
    assert (temp_data_path / "2.txt").is_file()
    data = h2.read(["1"], temp_data_path)
    assert len(data) == 1
    assert data["1"] == "1"
    delete_f(temp_data_path)


def test_report():
    s = h2.get_report(1, 1, "")
    assert s == "here is your report"
