import json
from pathlib import Path
from time import sleep
from typing import Any

from testy_quick import set_main_folder, SingleHandler
from testy_quick.end_functions import register_handler, create_test_case

set_main_folder("../fff")


class Person:
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname

    @create_test_case("t2", True, [("self", "person_handler")])
    def get_full_name(self) -> str:
        return f"{self.name} {self.surname}"


class PersonHandler(SingleHandler):
    def write_report(self, expected_answer: Any, actual_answer: Any, folder_path: Path, var_name) -> None:
        pass

    def is_same(self, expected_answer: Any, actual_answer: Any) -> bool:
        pass

    def user_def_read(self, var_name: str, folder_path: Path) -> Any:
        pass

    def user_def_write(self, var_name: str, var_value: Any, folder_path: Path) -> None:
        d = {"name": var_value.name, "surname": var_value.surname}
        with open(folder_path / (var_name + ".json"), "w") as f:
            json.dump(d, f, indent=2)


register_handler("person_handler", PersonHandler())

if __name__ == "__main__":
    p = Person("James", "Brown")
    s = p.get_full_name("dfs")
    print(s)
