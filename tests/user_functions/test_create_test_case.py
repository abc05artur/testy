import json
from pathlib import Path
from typing import Any

from tests.tools import temp_data_path, delete_f, reset_all
from testy_quick.end_functions import create_test_case, run_test_case
from testy_quick.strings import str_main_folder
from testy_quick.user_string import user_set_option, get_test_exists_function
from testy_quick.variable_handlers import SingleHandler, register_handler

user_set_option(str_main_folder, str(temp_data_path))


@create_test_case("sum", allow_multiple=True)
def sum(x, y):
    return x + y


@create_test_case("sum_diff", allow_multiple=True, treat_tuple_as_multiple_output=True)
def sum_diff(x, y):
    return x + y, x - y


class Person:
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname

    @create_test_case("get_full_name", False, [("self", "person_handler")])
    def get_full_name(self) -> str:
        return f"{self.name} {self.surname}"

    @create_test_case("set_name", False, [("self", "person_handler")])
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


def test_create_test_case():
    reset_all()
    sum(5, 9)
    try:
        sum("hello", 3)
    except:
        pass
    sum(10, 20)
    sum_diff(8, 9)
    sum_diff(-5, 9.5)


def test_case_method():
    p = Person("James", "Brown")
    p.set_name("Tom")
    p.get_full_name()
