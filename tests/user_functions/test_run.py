import json
from pathlib import Path
from typing import Any

from tests.tools import temp_data_path, temp_run_path, reset_run
from testy_quick.end_functions import create_tests_here
from testy_quick.strings import str_main_folder, str_run_folder_key
from testy_quick.user_string import user_set_option
from testy_quick.variable_handlers import SingleHandler, register_handler

user_set_option(str_main_folder, str(temp_data_path))
user_set_option(str_run_folder_key, str(temp_run_path))


def sum(x, y):
    print("sum")
    return x + y + 1


def sum_diff(x, y):
    print("sum_diff")
    return x + y, x - y


class Person:
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname

    def get_full_name(self) -> str:
        return f"{self.name} {self.surname}"

    def set_name(self, name) -> str:
        self.name = name


class PersonHandler(SingleHandler):
    def _write(self, var_name: str, var_value: Any, folder_path: Path) -> None:
        d = {"name": var_value.name, "surname": var_value.surname}
        folder_path.mkdir(parents=True, exist_ok=True)
        with open(folder_path / (var_name + ".json"), "w") as f:
            json.dump(d, f, indent=2)

    def _read(self, var_name: str, folder_path: Path) -> Any:
        with open(folder_path / (var_name + ".json"), "r") as f:
            d = json.load(f)
        return Person(**d)

    def _compare(self, expected_value: Any, actual_value: Any) -> bool:
        return expected_value.name == actual_value.name and expected_value.surname == actual_value.surname


register_handler("person_handler", PersonHandler())
reset_run()
create_tests_here(
    [
        (sum, ["sum/case_1", "sum/case_0", "sum/case_2", ]),
        (sum_diff, ["sum_diff/case_0", "sum_diff/case_1"]),
    ],
    # ["get_full_name", "set_name"],
)

if __name__ == "__main__":
    pass
