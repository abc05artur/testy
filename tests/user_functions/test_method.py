import json
from pathlib import Path
from typing import Any

from tests.tools import delete_f
from testy_quick.end_functions import create_test_case, run_test_case_method_unsafe
from testy_quick.strings import str_main_folder, str_run_folder_key
from testy_quick.user_string import user_set_option
from testy_quick.variable_handlers import SingleHandler, register_handler

user_set_option(str_main_folder, "../../temp_data")
user_set_option(str_run_folder_key, "../../temp_run")
# delete_f("../../temp_data")
delete_f("../../temp_run")


class Person:
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname

    # @create_test_case("t2", True, [("self", "person_handler")])
    def get_full_name(self) -> str:
        # self.name = "Martin"
        return f"{self.name} {self.surname}"


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


# p = Person("James", "Brown")
# p.get_full_name()
# s = p.get_full_name("dfs")
# print(s)


def test_p():
    run_test_case_method_unsafe("t2/case_0", "get_full_name")


def test_p1():
    run_test_case_method_unsafe("t2/case_1", "get_full_name")


if __name__ == "__main__":
    p = Person("James", "Brown")
    s = p.get_full_name("dfs")
    print(s)
